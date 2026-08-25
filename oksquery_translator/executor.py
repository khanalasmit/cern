"""
executor.py — Filter #2: Query Execution
==========================================

Executes a validated OksQuery against the real OKS engine and returns
ONLY the matching objects.  The full configuration is never exposed.

Two execution backends:
  1. Python ``config`` module (preferred — structured output)
  2. ``oks_dump`` CLI (fallback — parsed text)

Supports temporal version access via:
  - TDAQ_DB_PATH   (CVMFS snapshot, works on lxplus)
  - TDAQ_DB_VERSION (git hash/date, works on online nodes)
"""

import glob
import logging
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("oksquery_translator.executor")


class ExecutionResult:
    """Container for query execution results."""

    def __init__(self, success: bool, objects: List[Dict[str, Any]] = None,
                 count: int = 0, message: str = "",
                 version_used: str = ""):
        self.success = success
        self.objects = objects or []
        self.count = count
        self.message = message
        self.version_used = version_used

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "objects": self.objects,
            "count": self.count,
            "message": self.message,
            "version_used": self.version_used,
        }


class Executor:
    """
    Executes OksQuery strings and returns structured results.

    Usage::

        executor = Executor()
        result = executor.execute("Executable", '(all ("InitTimeout" "2" >))')
        for obj in result.objects:
            print(obj["id"], obj["attributes"])
    """

    def __init__(self, data_file: str = "daq/segments/setup.data.xml", repo_root: Optional[str] = None):
        self.data_file = data_file
        self.repo_root = repo_root or os.getcwd()
        self._config_available = self._check_config()
        self._oks_dump_path = shutil.which("oks_dump")

    def execute(self, target_class: str, query: str,
                version: str = None,
                max_objects: int = 200,
                data_file: Optional[str] = None,
                release: Optional[str] = None,
                partition: Optional[str] = None,
                repository: Optional[str] = None) -> ExecutionResult:
        """
        Execute a query and return matching objects.

        Parameters
        ----------
        target_class : str
            OKS class name.
        query : str
            Validated OksQuery string.
        version : str, optional
            Temporal version specifier (e.g. "hash:<sha>", "tag:r380689@all_hosts").
        max_objects : int
            Cap the number of returned objects.
        data_file : str, optional
            Data file path relative to OKS configuration repository.
        release : str, optional
            Target TDAQ release (e.g. "tdaq-11-02-01").
        partition : str, optional
            Partition name (e.g. "part_TGC_FillTest", "all_hosts").
        repository : str, optional
            Repository recorded with the run metadata.  This takes precedence
            over TDAQ_DB_REPOSITORY and over a URL derived from ``release``.

        Returns
        -------
        ExecutionResult
        """
        selected_data_file = data_file or self.data_file
        version_label = version or "current"
        is_historical = bool(version and version != "current")

        # Check for release mismatch between active environment and requested release
        active_release = os.environ.get("TDAQ_RELEASE")
        if release and active_release and release != active_release:
            logger.warning(
                f"Executor: Active TDAQ release is '{active_release}', but run specifies release '{release}'. "
                f"Query execution will proceed using active runtime '{active_release}' against historical revision '{version}'."
            )

        if is_historical:
            tdaq_repo = self._resolve_repository_url(release, partition, repository)
            if not tdaq_repo:
                msg = (
                    "Cannot load historical OKS configuration: "
                    "TDAQ_DB_REPOSITORY is not configured in the environment and could not be derived. "
                    "Historical configuration access requires TDAQ_DB_REPOSITORY to point to "
                    "the actual ATLAS OKS configuration Git repository."
                )
                logger.error(f"Executor: {msg}")
                return ExecutionResult(success=False, message=msg)

            if not selected_data_file:
                msg = "Cannot load historical OKS configuration: data_file path is missing."
                logger.error(f"Executor: {msg}")
                return ExecutionResult(success=False, message=msg)

            validation_error = self._validate_historical_configuration(
                repository=tdaq_repo, version=version, data_file=selected_data_file,
                release=release, partition=partition,
            )
            if validation_error:
                logger.error("Executor: historical configuration validation failed: %s", validation_error)
                return ExecutionResult(success=False, message=validation_error)

            logger.info(
                f"Executor: Historical configuration access:\n"
                f"  release: {release or 'unspecified'}\n"
                f"  partition: {partition or 'unspecified'}\n"
                f"  version: {version}\n"
                f"  data_file: {selected_data_file}\n"
                f"  TDAQ_DB_REPOSITORY: {tdaq_repo}\n"
                f"  OKS_GIT_PROTOCOL: ssh\n"
                f"  mode: historical Git-backed configuration"
            )
        else:
            user_repo = os.environ.get("TDAQ_DB_USER_REPOSITORY")
            if not user_repo and self.repo_root and os.path.exists(os.path.join(self.repo_root, selected_data_file)):
                user_repo = self.repo_root
            logger.info(
                f"Executor: Current configuration access:\n"
                f"  data_file: {selected_data_file}\n"
                f"  TDAQ_DB_USER_REPOSITORY: {user_repo or 'unset (using TDAQ_DB_PATH/release)'}\n"
                f"  mode: static/local current configuration"
            )

        oks_dump_path = self._oks_dump_path
        # A release-specific binary is only a fallback implementation detail.
        # Historical data itself is always selected from the Git repository.
        if not self._config_available and release:
            release_info = self._release_info(release)
            if release_info is not None:
                rel_dump_path, _ = release_info
                if not oks_dump_path:
                    oks_dump_path = rel_dump_path
            elif not oks_dump_path:
                return ExecutionResult(
                    success=False,
                    message=(
                        f"Recorded TDAQ release '{release}' is not available in CVMFS. "
                        "Cannot load this historical configuration."
                    ),
                )

        # Strategy 1 (preferred): Python config module.
        if self._config_available:
            env_backup = self._set_version_env(
                version, release=release, partition=partition, repository=repository
            )
            try:
                return self._execute_config(
                    target_class, query, max_objects, version_label, selected_data_file, version=version
                )
            except Exception as e:
                logger.warning(f"Executor: Python config backend failed ({e}); falling back to oks_dump CLI.")
            finally:
                self._restore_env(env_backup)

        # Strategy 2 (fallback): oks_dump CLI.
        if oks_dump_path:
            return self._execute_oks_dump(
                target_class, query, max_objects, version_label, selected_data_file,
                oks_dump_path,
                version=version,
                release=release,
                partition=partition,
                repository=repository,
            )

        return ExecutionResult(
            success=False,
            message=(
                "No execution backend available. "
                "Ensure the TDAQ release is sourced "
                "(source .../setup.sh) so that the Python 'config' module "
                "and/or 'oks_dump' are available."
            ),
        )

    # ------------------------------------------------------------------
    # Config module execution
    # ------------------------------------------------------------------

    def _execute_config(self, target_class: str, query: str,
                        max_objects: int, version_label: str,
                        data_file: str, version: Optional[str] = None) -> ExecutionResult:
        """Execute via the Python config module."""
        import config as oks_config

        logger.info(f"Executor: Executing via Python C++ config backend -> class={target_class!r}, query={query!r}, data_file={data_file!r}, version={version!r}")
        t_start = time.perf_counter()

        conn_spec = data_file
        if version and version != "current" and "&version=" not in conn_spec:
            conn_spec = f"{data_file}&version={version}"

        db = None
        last_err = None
        for prefix in ("oksconfig:", "oksconflibs:"):
            try:
                db = oks_config.Configuration(f"{prefix}{conn_spec}")
                break
            except Exception as e:
                logger.warning(f"Executor: Configuration('{prefix}{conn_spec}') failed: {e}")
                last_err = e
                continue
        if db is None:
            raise last_err or RuntimeError(f"Could not initialize Configuration for {conn_spec}")

        raw_objects = db.get_objs(target_class, query)

        objects = []
        for obj in raw_objects:
            if len(objects) >= max_objects:
                break
            obj_dict = {
                "id": obj.UID(),
                "class": target_class,
                "attributes": {},
            }
            # Try to read common attributes
            try:
                attrs = db.attributes(target_class)
                if isinstance(attrs, dict):
                    for aname in attrs:
                        try:
                            obj_dict["attributes"][aname] = str(
                                getattr(obj, aname, "")
                            )
                        except Exception:
                            pass
                elif isinstance(attrs, (list, tuple)):
                    for a in attrs:
                        aname = a if isinstance(a, str) else a.get("name", "")
                        if aname:
                            try:
                                obj_dict["attributes"][aname] = str(
                                    getattr(obj, aname, "")
                                )
                            except Exception:
                                pass
            except Exception:
                pass

            objects.append(obj_dict)

        total_count = len(objects)
        elapsed = time.perf_counter() - t_start
        logger.info(f"Executor: Python C++ config backend returned {total_count} object(s) in {elapsed:.3f}s")

        return ExecutionResult(
            success=True,
            objects=objects,
            count=total_count,
            version_used=version_label,
        )

    # ------------------------------------------------------------------
    # oks_dump CLI execution
    # ------------------------------------------------------------------

    @staticmethod
    def _get_release_ld_paths(oks_dump_path: str) -> List[str]:
        """
        Discover library paths required by an oks_dump binary in CVMFS,
        including architecture-specific lib directories and static OpenSSL locations.
        """
        ld_paths = []
        if oks_dump_path:
            bin_dir = os.path.dirname(oks_dump_path)
            arch_dir = os.path.dirname(bin_dir)
            arch_lib = os.path.join(arch_dir, "lib")
            if os.path.isdir(arch_lib):
                ld_paths.append(arch_lib)

        # Static common CVMFS SSL lib locations (avoiding expensive wildcard globbing on network filesystem)
        static_ssl_paths = [
            "/cvmfs/sft.cern.ch/lcg/external/OpenSSL/1.0.2o/x86_64-centos7-gcc8-opt/lib",
            "/cvmfs/sft.cern.ch/lcg/releases/LCG_96/OpenSSL/1.0.2o/x86_64-centos7-gcc8-opt/lib",
        ]
        for p in static_ssl_paths:
            if os.path.isdir(p) and p not in ld_paths:
                ld_paths.append(p)

        return ld_paths

    @staticmethod
    def _normalize_repository_url(url: Optional[str]) -> Optional[str]:
        """
        Ensure CERN GitLab SSH URLs explicitly specify port 7999.
        Preserves HTTPS URLs and non-CERN URLs.
        """
        if not url:
            return url

        if "gitlab.cern.ch" in url and not url.startswith("https://"):
            if "gitlab.cern.ch:7999" not in url:
                if url.startswith("ssh://git@gitlab.cern.ch/"):
                    return url.replace("ssh://git@gitlab.cern.ch/", "ssh://git@gitlab.cern.ch:7999/", 1)
                elif url.startswith("git@gitlab.cern.ch:"):
                    return url.replace("git@gitlab.cern.ch:", "ssh://git@gitlab.cern.ch:7999/", 1)

        return url

    @classmethod
    def _resolve_repository_url(cls, release: Optional[str], partition: Optional[str] = None,
                                repository: Optional[str] = None) -> Optional[str]:
        """
        Resolve the official ATLAS OKS configuration Git repository URL.

        Precedence:
          1. Repository supplied by run metadata
          2. Environment variable TDAQ_DB_REPOSITORY
          3. Auto-derived SSH URL (with port 7999) based on OKS_GIT_PROTOCOL, family and release.
        """
        url = None
        if repository:
            url = repository
        else:
            env_repo = os.environ.get("TDAQ_DB_REPOSITORY")
            if env_repo:
                url = env_repo

        if url:
            return cls._normalize_repository_url(url)

        if not release:
            return None

        part = (partition or "").lower()
        if part in ("all_hosts", "tbed", "testbed"):
            family = "tbed"
        else:
            family = "p1"

        protocol = os.environ.get("OKS_GIT_PROTOCOL", "ssh").lower()
        if protocol == "ssh":
            return f"ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/{family}/{release}.git"
        else:
            return f"https://gitlab.cern.ch/atlas-tdaq-oks/{family}/{release}.git"

    @staticmethod
    def _validate_historical_configuration(repository: str, version: str,
                                           data_file: str, release: Optional[str],
                                           partition: Optional[str]) -> Optional[str]:
        """Verify the exact revision and file before the OKS kernel is opened.

        A temporary Git repository is used so that validation neither relies on
        the active TDAQ checkout nor changes a caller's Git working tree.
        ``git fetch <revision>`` works for both ``tag:<name>`` and
        ``hash:<sha>`` and ``git cat-file`` verifies the configuration path at
        precisely that fetched commit.
        """
        if not version.startswith(("tag:", "hash:")):
            return ("revision resolution failed: historical version must be "
                    "'tag:<tag>' or 'hash:<sha>'; got %r" % version)
        if not data_file or os.path.isabs(data_file) or ".." in data_file.split("/"):
            return "data-file resolution failed: data_file must be a relative repository path"

        revision = version.split(":", 1)[1]
        if not revision:
            return "revision resolution failed: empty tag/SHA"
        try:
            with tempfile.TemporaryDirectory(prefix="oks-history-validate-") as temp_dir:
                def git(*args: str) -> subprocess.CompletedProcess:
                    env = os.environ.copy()
                    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new"
                    return subprocess.run(
                        ["git", *args], cwd=temp_dir, capture_output=True,
                        text=True, timeout=45, env=env,
                    )

                init = git("init", "--quiet")
                if init.returncode:
                    return "repository resolution failed: could not initialize isolated Git validation"
                add = git("remote", "add", "origin", repository)
                if add.returncode:
                    return "repository resolution failed: could not configure repository %r" % repository

                if version.startswith("tag:"):
                    fetch_ref = f"refs/tags/{revision}"
                else:
                    fetch_ref = revision

                fetched = git("fetch", "--quiet", "--depth=1", "origin", fetch_ref)
                if fetched.returncode:
                    fetched = git("fetch", "--quiet", "origin", fetch_ref)

                if fetched.returncode:
                    detail = (fetched.stderr or fetched.stdout).strip()
                    return ("revision resolution failed: %s is not available in repository %s"
                            "%s" % (version, repository, (": " + detail) if detail else ""))
                resolved = git("rev-parse", "--verify", "FETCH_HEAD^{commit}")
                if resolved.returncode:
                    return "revision resolution failed: %s did not resolve to a commit" % version
                present = git("cat-file", "-e", "FETCH_HEAD:%s" % data_file)
                if present.returncode:
                    return ("data-file resolution failed: %s is absent at %s in repository %s"
                            % (data_file, version, repository))
        except subprocess.TimeoutExpired:
            return "repository/revision resolution failed: Git validation timed out"
        except OSError as exc:
            return "repository resolution failed: unable to invoke git: %s" % exc
        return None

    def _execute_oks_dump(self, target_class: str, query: str,
                          max_objects: int, version_label: str,
                          data_file: str, oks_dump_path: str,
                          version: str = None,
                          release: str = None,
                          partition: str = None,
                          repository: str = None) -> ExecutionResult:
        """Execute via oks_dump CLI and parse the output."""
        import shlex

        # Prepare environment — start from caller's full environment so that
        # TDAQ_DB_REPOSITORY etc. are inherited.
        env = os.environ.copy()

        if version and version != "current":
            repo_url = self._resolve_repository_url(release, partition, repository)
            if repo_url:
                env["TDAQ_DB_REPOSITORY"] = repo_url
                env["OKS_GIT_PROTOCOL"] = os.environ.get("OKS_GIT_PROTOCOL", "ssh")

            env.pop("TDAQ_DB_USER_REPOSITORY", None)
            env.pop("TDAQ_DB_PATH", None)

            if not env.get("TDAQ_DB_REPOSITORY"):
                return ExecutionResult(
                    success=False,
                    message=(
                        "Cannot load historical OKS configuration: "
                        "TDAQ_DB_REPOSITORY is not configured in the environment. "
                        "Historical configuration access requires TDAQ_DB_REPOSITORY to point to "
                        "the actual ATLAS OKS configuration Git repository."
                    ),
                )
            if version.startswith(("hash:", "date:", "tag:")):
                env["TDAQ_DB_VERSION"] = version
                logger.info(f"Executor: Setting TDAQ_DB_VERSION={version!r} in subprocess env")
            elif version.startswith("run:") or (version.startswith("r") and version[1:].isdigit()):
                run_num = version.split(":")[-1].lstrip("r")
                part = partition or "all_hosts"
                tag_name = f"tag:r{run_num}@{part}"
                env["TDAQ_DB_VERSION"] = tag_name
                logger.info(f"Executor: Setting TDAQ_DB_VERSION={tag_name!r} in subprocess env (from {version!r})")
        else:
            user_repo = env.get("TDAQ_DB_USER_REPOSITORY", "")
            if not user_repo and self.repo_root:
                local_file = os.path.join(self.repo_root, data_file)
                if os.path.exists(local_file):
                    env["TDAQ_DB_USER_REPOSITORY"] = self.repo_root
                    logger.info(f"Executor: Set TDAQ_DB_USER_REPOSITORY={self.repo_root!r} for current query")
                else:
                    env.pop("TDAQ_DB_USER_REPOSITORY", None)

        extra_ld_paths = self._get_release_ld_paths(oks_dump_path)
        if extra_ld_paths:
            existing_ld = env.get("LD_LIBRARY_PATH", "")
            all_ld_paths = extra_ld_paths + ([existing_ld] if existing_ld else [])
            env["LD_LIBRARY_PATH"] = ":".join(all_ld_paths)

        # Extract architecture directory name (e.g. x86_64-centos7-gcc11-dbg)
        bin_dir = os.path.dirname(oks_dump_path)
        arch_dir = os.path.dirname(bin_dir)
        arch_name = os.path.basename(arch_dir)
        installed_dir = os.path.dirname(arch_dir)

        if arch_name and arch_name != "installed":
            env["CMTCONFIG"] = arch_name
            env["BINARY_TAG"] = arch_name
            env["ATLAS_BUILD_TARGET"] = arch_name

        # Check if a setup script exists for the release
        setup_script = None
        for candidate in [
            os.path.join(arch_dir, "setup.sh"),
            os.path.join(installed_dir, "setup.sh"),
            os.path.join(os.path.dirname(installed_dir), "setup.sh"),
        ]:
            if os.path.isfile(candidate):
                setup_script = candidate
                break

        conn_spec = data_file
        if version and version != "current" and "&version=" not in conn_spec:
            conn_spec = f"{data_file}&version={version}"

        cmd = [oks_dump_path, "-c", target_class, "-q", query, conn_spec]
        cmd_display = " ".join(shlex.quote(arg) for arg in cmd)

        t_start = time.perf_counter()
        try:
            logger.info(f"Executor: Executing direct oks_dump binary:\n  $ {cmd_display}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60, env=env
            )

            if result.returncode not in (0, 5) and setup_script:
                logger.info(f"Executor: Direct binary execution returned exit {result.returncode}; retrying via setup script...")
                env_exports = ""
                if arch_name and arch_name != "installed":
                    env_exports = f"export CMTCONFIG={shlex.quote(arch_name)}; export BINARY_TAG={shlex.quote(arch_name)}; "
                shell_cmd = f"{env_exports}source {shlex.quote(setup_script)} && {cmd_display}"
                result = subprocess.run(
                    ["bash", "-c", shell_cmd],
                    capture_output=True, text=True, timeout=60, env=env
                )
        except subprocess.TimeoutExpired:
            logger.error("Executor: oks_dump CLI timed out after 60s.")
            return ExecutionResult(
                success=False,
                message="oks_dump timed out after 60s.",
            )
        except OSError as exc:
            logger.error(f"Executor: Unable to start oks_dump: {exc}")
            return ExecutionResult(
                success=False,
                message=f"Unable to start oks_dump '{oks_dump_path}': {exc}",
            )

        elapsed = time.perf_counter() - t_start

        if result.returncode not in (0, 5):
            logger.error(f"Executor: oks_dump failed with exit code {result.returncode} in {elapsed:.3f}s:\n{result.stderr.strip()}")
            return ExecutionResult(
                success=False,
                message=f"oks_dump failed (exit {result.returncode}): "
                        f"{result.stderr.strip()}",
            )

        objects = self._parse_oks_dump_output(result.stdout, target_class)
        logger.info(f"Executor: oks_dump succeeded (exit {result.returncode}) in {elapsed:.3f}s. Extracted {len(objects)} matching object(s).")

        return ExecutionResult(
            success=True,
            objects=objects[:max_objects],
            count=len(objects),
            version_used=version_label,
        )

    @staticmethod
    def _parse_oks_dump_output(output: str, target_class: str) -> List[Dict]:
        """
        Parse oks_dump query output to extract matching objects.

        The output format for queried objects is typically:
          Object "obj-id@ClassName"
            attribute-name: value
            ...
        """
        objects = []
        current_obj = None

        for line in output.splitlines():
            stripped = line.strip()

            # Match object header: Object "id@Class" or similar
            obj_match = re.match(
                r'^\s*Object\s+"([^"]+?)(?:@[^"]+)?"', line
            )
            if obj_match:
                if current_obj is not None:
                    objects.append(current_obj)
                current_obj = {
                    "id": obj_match.group(1),
                    "class": target_class,
                    "attributes": {},
                }
                continue

            # Match attribute lines (indented, with key: value)
            if current_obj is not None and ":" in stripped:
                attr_match = re.match(r'^(\w[\w\s]*\w|\w+)\s*:\s*(.*)', stripped)
                if attr_match:
                    key = attr_match.group(1).strip()
                    value = attr_match.group(2).strip()
                    # Skip internal fields
                    if key not in ("oks-file", "oks-type"):
                        current_obj["attributes"][key] = value

        if current_obj is not None:
            objects.append(current_obj)

        return objects

    # ------------------------------------------------------------------
    # Temporal version environment
    # ------------------------------------------------------------------

    def _set_version_env(self, version: Optional[str],
                         release: Optional[str] = None,
                         partition: Optional[str] = None,
                         repository: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Set environment variables for temporal access.
        Returns backup of original values for restoration.
        """
        backup: Dict[str, Optional[str]] = {}

        if version and version != "current":
            repo_url = self._resolve_repository_url(release, partition, repository)
            if repo_url:
                backup["TDAQ_DB_REPOSITORY"] = os.environ.get("TDAQ_DB_REPOSITORY")
                os.environ["TDAQ_DB_REPOSITORY"] = repo_url
                backup["OKS_GIT_PROTOCOL"] = os.environ.get("OKS_GIT_PROTOCOL")
                os.environ["OKS_GIT_PROTOCOL"] = os.environ.get("OKS_GIT_PROTOCOL", "ssh")

            if "TDAQ_DB_USER_REPOSITORY" in os.environ:
                backup["TDAQ_DB_USER_REPOSITORY"] = os.environ.get("TDAQ_DB_USER_REPOSITORY")
                del os.environ["TDAQ_DB_USER_REPOSITORY"]

            if "TDAQ_DB_PATH" in os.environ:
                backup["TDAQ_DB_PATH"] = os.environ.get("TDAQ_DB_PATH")
                del os.environ["TDAQ_DB_PATH"]
        else:
            if "TDAQ_DB_USER_REPOSITORY" not in os.environ and self.repo_root:
                local_file = os.path.join(self.repo_root, self.data_file)
                if os.path.exists(local_file):
                    backup["TDAQ_DB_USER_REPOSITORY"] = None
                    os.environ["TDAQ_DB_USER_REPOSITORY"] = self.repo_root

        if not version or version == "current":
            return backup

        if (version.startswith("hash:") or version.startswith("date:") or 
            version.startswith("tag:")):
            backup["TDAQ_DB_VERSION"] = os.environ.get("TDAQ_DB_VERSION")
            os.environ["TDAQ_DB_VERSION"] = version
        elif version.startswith("run:") or (version.startswith("r") and version[1:].isdigit()):
            run_num = version.split(":")[-1].lstrip("r")
            part = partition or "all_hosts"
            tag_name = f"tag:r{run_num}@{part}"
            backup["TDAQ_DB_VERSION"] = os.environ.get("TDAQ_DB_VERSION")
            os.environ["TDAQ_DB_VERSION"] = tag_name
        return backup

    @staticmethod
    def _restore_env(backup: Dict[str, Optional[str]]):
        """Restore environment variables from backup."""
        for key, value in backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    @staticmethod
    def _release_info(release: str) -> Optional[tuple[str, str]]:
        """Return the release-specific ``oks_dump`` and data directory.

        TDAQ installations put the binary under an architecture-specific
        directory, while data is shared under ``installed/share/data``.
        """
        if not re.fullmatch(r"tdaq-\d{2}-\d{2}-\d{2}", release or ""):
            return None

        installed = f"/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/{release}/installed"
        data_dir = os.path.join(installed, "share", "data")
        candidates = sorted(glob.glob(os.path.join(installed, "*", "bin", "oks_dump")))
        if not os.path.isdir(data_dir) or not candidates:
            return None

        host_arch = platform.machine().lower()
        # CVMFS releases can contain several architectures.  A lexical sort
        # would select aarch64 before x86_64 and produces Exec format error on
        # lxplus x86_64 nodes.
        matching = [path for path in candidates
                    if os.path.basename(os.path.dirname(os.path.dirname(path))).lower().startswith(host_arch + "-")]
        return (matching[0] if matching else candidates[0]), data_dir

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_config() -> bool:
        try:
            import config  # noqa: F401
            return True
        except ImportError:
            return False
