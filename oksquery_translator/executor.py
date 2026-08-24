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
import os
import platform
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional


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

    def __init__(self, data_file: str = "daq/segments/setup.data.xml"):
        self.data_file = data_file
        self._config_available = self._check_config()
        self._oks_dump_path = shutil.which("oks_dump")

    def execute(self, target_class: str, query: str,
                version: str = None,
                max_objects: int = 200,
                data_file: Optional[str] = None,
                release: Optional[str] = None) -> ExecutionResult:
        """
        Execute a query and return matching objects.

        Parameters
        ----------
        target_class : str
            OKS class name.
        query : str
            Validated OksQuery string.
        version : str, optional
            Temporal version specifier:
              - "hash:<commit>"  → sets TDAQ_DB_VERSION
              - "date:<date>"    → sets TDAQ_DB_VERSION
              - "tdaq-XX-YY-ZZ"  → sets TDAQ_DB_PATH to CVMFS snapshot
        max_objects : int
            Cap the number of returned objects.

        Returns
        -------
        ExecutionResult
        """
        # A run-number DB record may identify a different top-level data file.
        # Keep the instance default for ordinary/current queries.
        selected_data_file = data_file or self.data_file

        # A historical run may have been recorded with a different TDAQ
        # release.  Do not run its data file through the caller's current
        # release: locate that release's own oks_dump and data repository.
        oks_dump_path = self._oks_dump_path
        if release:
            release_info = self._release_info(release)
            if release_info is None:
                return ExecutionResult(
                    success=False,
                    message=(
                        f"Recorded TDAQ release '{release}' is not available in CVMFS. "
                        "Cannot load this historical configuration."
                    ),
                )
            oks_dump_path, release_data_path = release_info
        else:
            release_data_path = None

        # Set up temporal environment if needed
        env_backup = self._set_version_env(version, release_data_path)
        version_label = version or "current"

        try:
            # Strategy 1: Python config module
            if self._config_available and not release:
                try:
                    return self._execute_config(
                        target_class, query, max_objects, version_label, selected_data_file
                    )
                except Exception as e:
                    # Fall through to oks_dump
                    pass

            # Strategy 2: oks_dump CLI
            if oks_dump_path:
                return self._execute_oks_dump(
                    target_class, query, max_objects, version_label, selected_data_file,
                    oks_dump_path,
                )

            return ExecutionResult(
                success=False,
                message=(
                    "No execution backend available. "
                    "Ensure the TDAQ release is sourced "
                    "(source .../setup.sh) so that 'oks_dump' and/or "
                    "the Python 'config' module are available."
                ),
            )
        finally:
            self._restore_env(env_backup)

    # ------------------------------------------------------------------
    # Config module execution
    # ------------------------------------------------------------------

    def _execute_config(self, target_class: str, query: str,
                        max_objects: int, version_label: str,
                        data_file: str) -> ExecutionResult:
        """Execute via the Python config module."""
        import config as oks_config

        db = oks_config.Configuration("oksconflibs:" + data_file)
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

        total_count = len(list(raw_objects)) if hasattr(raw_objects, '__len__') else len(objects)

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
        including architecture-specific lib directories and OpenSSL 1.0 (libssl.so.10)
        fallback locations in CVMFS.
        """
        ld_paths = []
        if oks_dump_path:
            bin_dir = os.path.dirname(oks_dump_path)
            arch_dir = os.path.dirname(bin_dir)
            arch_lib = os.path.join(arch_dir, "lib")
            if os.path.isdir(arch_lib):
                ld_paths.append(arch_lib)

        # Search CVMFS for OpenSSL 1.0 (libssl.so.10) directories
        cvmfs_ssl_patterns = [
            "/cvmfs/sft.cern.ch/lcg/external/OpenSSL/*/x86_64-*/lib",
            "/cvmfs/sft.cern.ch/lcg/releases/LCG_*/OpenSSL/*/x86_64-*/lib",
            "/cvmfs/sft.cern.ch/lcg/contrib/openssl/*/lib",
            "/cvmfs/sft.cern.ch/lcg/views/*/x86_64-*/lib",
            "/cvmfs/atlas.cern.ch/repo/sw/software/*/lib",
            "/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/*/installed/x86_64-*/lib",
        ]
        for pattern in cvmfs_ssl_patterns:
            for p in glob.glob(pattern):
                if os.path.isdir(p) and (
                    os.path.exists(os.path.join(p, "libssl.so.10")) or
                    os.path.exists(os.path.join(p, "libssl.so.1.0.0"))
                ):
                    if p not in ld_paths:
                        ld_paths.append(p)
                        break

        return ld_paths

    def _execute_oks_dump(self, target_class: str, query: str,
                          max_objects: int, version_label: str,
                          data_file: str, oks_dump_path: str) -> ExecutionResult:
        """Execute via oks_dump CLI and parse the output."""
        import shlex

        # Prepare environment with enriched LD_LIBRARY_PATH
        env = os.environ.copy()
        extra_ld_paths = self._get_release_ld_paths(oks_dump_path)
        if extra_ld_paths:
            existing_ld = env.get("LD_LIBRARY_PATH", "")
            all_ld_paths = extra_ld_paths + ([existing_ld] if existing_ld else [])
            env["LD_LIBRARY_PATH"] = ":".join(all_ld_paths)

        # Check if a setup script exists for the release
        bin_dir = os.path.dirname(oks_dump_path)
        arch_dir = os.path.dirname(bin_dir)
        installed_dir = os.path.dirname(arch_dir)

        setup_script = None
        for candidate in [
            os.path.join(arch_dir, "setup.sh"),
            os.path.join(installed_dir, "setup.sh"),
            os.path.join(os.path.dirname(installed_dir), "setup.sh"),
        ]:
            if os.path.isfile(candidate):
                setup_script = candidate
                break

        cmd = [oks_dump_path, "-c", target_class, "-q", query, data_file]

        try:
            if setup_script:
                cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
                shell_cmd = f"source {shlex.quote(setup_script)} && {cmd_str}"
                result = subprocess.run(
                    ["bash", "-c", shell_cmd],
                    capture_output=True, text=True, timeout=60, env=env
                )
            else:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60, env=env
                )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                message="oks_dump timed out after 60s.",
            )
        except OSError as exc:
            return ExecutionResult(
                success=False,
                message=f"Unable to start oks_dump '{oks_dump_path}': {exc}",
            )

        if result.returncode not in (0, 5):
            return ExecutionResult(
                success=False,
                message=f"oks_dump failed (exit {result.returncode}): "
                        f"{result.stderr.strip()}",
            )

        objects = self._parse_oks_dump_output(result.stdout, target_class)

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

    @staticmethod
    def _set_version_env(version: str,
                         release_data_path: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Set environment variables for temporal access.
        Returns backup of original values for restoration.
        """
        backup = {}
        if release_data_path:
            backup["TDAQ_DB_PATH"] = os.environ.get("TDAQ_DB_PATH")
            os.environ["TDAQ_DB_PATH"] = release_data_path

        if not version:
            return backup

        if (version.startswith("hash:") or version.startswith("date:") or 
            version.startswith("tag:")):
            backup["TDAQ_DB_VERSION"] = os.environ.get("TDAQ_DB_VERSION")
            os.environ["TDAQ_DB_VERSION"] = version
        elif version.startswith("run:") or (version.startswith("r") and version[1:].isdigit()):
            # Run number format, e.g. "run:454833" or "r454833" -> "tag:r454833@ATLAS"
            run_num = version.split(":")[-1].lstrip("r")
            tag_name = f"tag:r{run_num}@ATLAS"
            backup["TDAQ_DB_VERSION"] = os.environ.get("TDAQ_DB_VERSION")
            os.environ["TDAQ_DB_VERSION"] = tag_name
        elif version.startswith("tdaq-"):
            # CVMFS snapshot
            snapshot_path = (
                f"/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/{version}"
                f"/installed/share/data"
            )
            if "TDAQ_DB_PATH" not in backup:
                backup["TDAQ_DB_PATH"] = os.environ.get("TDAQ_DB_PATH")
            os.environ["TDAQ_DB_PATH"] = snapshot_path

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
