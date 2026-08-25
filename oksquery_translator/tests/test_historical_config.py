"""
test_historical_config.py — Historical Configuration Resolution Tests
======================================================================

Tests the 8 required test cases for historical OKS configuration access:
  1. Preserving TDAQ_DB_REPOSITORY from environment (not replacing with translator repo).
  2. Failing early with clear error when TDAQ_DB_REPOSITORY is missing.
  3. Propagating TDAQ_DB_VERSION correctly to the execution environment.
  4. Preserving the exact historical data_file path (e.g. muons/partitions/part_TGC_FillTest.data.xml).
  5. Not forcing TDAQ_DB_PATH to release installed/share/data for historical queries.
  6. Removing TDAQ_DB_USER_REPOSITORY for historical queries.
  7. Passing correct env (TDAQ_DB_REPOSITORY, TDAQ_DB_VERSION) to oks_dump subprocess.
  8. Logging a release mismatch warning when active TDAQ_RELEASE differs from run release.
"""

import logging
import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from oksquery_translator.executor import Executor, ExecutionResult


class TestHistoricalConfig(unittest.TestCase):
    """Test suite for historical OKS configuration loading in Executor."""

    def setUp(self):
        self.translator_repo = "/path/to/translator/project"
        self.executor = Executor(
            data_file="daq/segments/setup.data.xml",
            repo_root=self.translator_repo,
        )
        self.executor._config_available = True
        self.executor._oks_dump_path = "/fake/oks_dump"
        # Most tests below exercise environment wiring, not Git transport.
        self.executor._validate_historical_configuration = MagicMock(return_value=None)

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository"}, clear=True)
    def test_1_historical_repository_preserved(self):
        """Test 1: Given TDAQ_DB_REPOSITORY=/actual/config/repository, executor preserves it."""
        with patch.object(self.executor, "_execute_config") as mock_exec_config:
            mock_exec_config.return_value = ExecutionResult(success=True, count=1)
            
        with patch.object(self.executor, "_execute_oks_dump") as mock_exec:
            mock_exec.return_value = ExecutionResult(success=True, count=1)

            res = self.executor.execute(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
                data_file="muons/partitions/part_TGC_FillTest.data.xml",
            )
            

            self.assertTrue(res.success)
            self.assertEqual(os.environ.get("TDAQ_DB_REPOSITORY"), "/actual/config/repository")
            self.assertNotEqual(os.environ.get("TDAQ_DB_REPOSITORY"), self.translator_repo)

    @patch.dict(os.environ, {}, clear=True)
    def test_2_missing_historical_repository_fails_early(self):
        """Test 2: Given missing TDAQ_DB_REPOSITORY, historical execution fails early with clear error."""
        res = self.executor.execute(
            target_class="Application",
            query='(all ("InitTimeout" "30" >))',
            version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            data_file="muons/partitions/part_TGC_FillTest.data.xml",
        )
        

        self.assertFalse(res.success)
        self.assertIn("TDAQ_DB_REPOSITORY is not configured", res.message)
        self.assertIn("Historical configuration access requires TDAQ_DB_REPOSITORY", res.message)
        # Verify self.repo_root was NOT set into os.environ
        self.assertIsNone(os.environ.get("TDAQ_DB_REPOSITORY"))

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository"}, clear=True)
    def test_3_historical_version_propagation(self):
        """Test 3: TDAQ_DB_VERSION is passed correctly to environment during execution."""
        sha = "hash:c85894a53e0e17911015fbefdfce33679f41e2ff"
        captured_version_env = None

        def side_effect(*args, **kwargs):
            nonlocal captured_version_env
            captured_version_env = os.environ.get("TDAQ_DB_VERSION")
            return ExecutionResult(success=True, count=1)
        with patch.object(self.executor, "_execute_oks_dump") as mock_exec:
            mock_exec.return_value = ExecutionResult(success=True, count=1)

        with patch.object(self.executor, "_execute_config", side_effect=side_effect):
            res = self.executor.execute(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                version=sha,
                data_file="muons/partitions/part_TGC_FillTest.data.xml",
            )
            self.assertTrue(res.success)
            self.assertEqual(captured_version_env, sha)
            call_kwargs = mock_exec.call_args.kwargs
            self.assertEqual(call_kwargs.get("version"), sha)

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository"}, clear=True)
    def test_4_historical_data_file_preserved(self):
        """Test 4: Historical data_file (muons/partitions/part_TGC_FillTest.data.xml) is passed unchanged."""
        hist_file = "muons/partitions/part_TGC_FillTest.data.xml"
        captured_data_file = None

        def side_effect(target_class, query, max_objects, version_label, data_file, version=None):
            nonlocal captured_data_file
            captured_data_file = data_file
            return ExecutionResult(success=True, count=1)
        with patch.object(self.executor, "_execute_oks_dump") as mock_exec:
            mock_exec.return_value = ExecutionResult(success=True, count=1)

        with patch.object(self.executor, "_execute_config", side_effect=side_effect):
            res = self.executor.execute(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
                data_file=hist_file,
            )
            self.assertTrue(res.success)
            self.assertEqual(captured_data_file, hist_file)
            self.assertNotEqual(captured_data_file, "daq/segments/setup.data.xml")
            call_args = mock_exec.call_args
            passed_data_file = call_args.args[4] if call_args.args else call_args.kwargs.get("data_file")
            self.assertEqual(passed_data_file, hist_file)
            self.assertNotEqual(passed_data_file, "daq/segments/setup.data.xml")

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository"}, clear=True)
    def test_5_tdaq_db_path_not_forced(self):
    @patch("subprocess.run")
    def test_5_tdaq_db_path_not_forced(self, mock_run):
        """Test 5: TDAQ_DB_PATH is not forced to installed/share/data for historical queries."""
        captured_db_path = None
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        def side_effect(*args, **kwargs):
            nonlocal captured_db_path
            captured_db_path = os.environ.get("TDAQ_DB_PATH")
            return ExecutionResult(success=True, count=1)
        res = self.executor._execute_oks_dump(
            target_class="Application",
            query='(all ("InitTimeout" "30" >))',
            max_objects=10,
            version_label="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            data_file="muons/partitions/part_TGC_FillTest.data.xml",
            oks_dump_path="/usr/bin/oks_dump",
            version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            release="tdaq-11-02-01",
        )
        self.assertTrue(res.success)
        sub_env = mock_run.call_args[1].get("env", {})
        self.assertNotIn("TDAQ_DB_PATH", sub_env)

        self.executor._oks_dump_path = "/usr/bin/oks_dump"
        with patch.object(self.executor, "_execute_config", side_effect=side_effect):
            res = self.executor.execute(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
                data_file="muons/partitions/part_TGC_FillTest.data.xml",
                release="tdaq-11-02-01",
            )
            self.assertTrue(res.success)
            self.assertIsNone(captured_db_path)

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository", "TDAQ_DB_USER_REPOSITORY": "/some/local/repo"}, clear=True)
    def test_6_user_repository_removed_for_historical(self):
    @patch("subprocess.run")
    def test_6_user_repository_removed_for_historical(self, mock_run):
        """Test 6: TDAQ_DB_USER_REPOSITORY is removed during historical resolution."""
        captured_user_repo = "NOT_CHECKED"
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        def side_effect(*args, **kwargs):
            nonlocal captured_user_repo
            captured_user_repo = os.environ.get("TDAQ_DB_USER_REPOSITORY")
            return ExecutionResult(success=True, count=1)
        res = self.executor._execute_oks_dump(
            target_class="Application",
            query='(all ("InitTimeout" "30" >))',
            max_objects=10,
            version_label="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            data_file="muons/partitions/part_TGC_FillTest.data.xml",
            oks_dump_path="/usr/bin/oks_dump",
            version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
        )
        self.assertTrue(res.success)
        sub_env = mock_run.call_args[1].get("env", {})
        self.assertNotIn("TDAQ_DB_USER_REPOSITORY", sub_env)

        with patch.object(self.executor, "_execute_config", side_effect=side_effect):
            res = self.executor.execute(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
                data_file="muons/partitions/part_TGC_FillTest.data.xml",
            )
            self.assertTrue(res.success)
            self.assertIsNone(captured_user_repo)

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository", "TDAQ_DB_USER_REPOSITORY": "/local/repo"}, clear=True)
    @patch("subprocess.run")
    def test_7_subprocess_environment_for_oks_dump(self, mock_run):
        """Test 7: Subprocess for oks_dump receives TDAQ_DB_REPOSITORY and TDAQ_DB_VERSION."""
        mock_run.return_value = MagicMock(returncode=0, stdout='Object "app1@Application"\n  InitTimeout: 40\n')
        
        # Disable python config module to force oks_dump CLI fallback
        with patch.object(self.executor, "_config_available", False):
            res = self.executor._execute_oks_dump(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                max_objects=10,
                version_label="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
                data_file="muons/partitions/part_TGC_FillTest.data.xml",
                oks_dump_path="/usr/bin/oks_dump",
                version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            )
            self.assertTrue(res.success)
            self.assertTrue(mock_run.called)
            
            # Extract env passed to subprocess.run
            call_kwargs = mock_run.call_args[1]
            sub_env = call_kwargs.get("env", {})
            
            self.assertEqual(sub_env.get("TDAQ_DB_REPOSITORY"), "/actual/config/repository")
            self.assertEqual(sub_env.get("TDAQ_DB_VERSION"), "hash:c85894a53e0e17911015fbefdfce33679f41e2ff")
            self.assertNotIn("TDAQ_DB_USER_REPOSITORY", sub_env)

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "/actual/config/repository", "TDAQ_RELEASE": "tdaq-12-00-00"}, clear=True)
    def test_8_release_mismatch_warning(self):
        """Test 8: Release mismatch between active TDAQ_RELEASE and run release logs a warning."""
        self.executor._oks_dump_path = "/usr/bin/oks_dump"
        with patch.object(self.executor, "_execute_config") as mock_exec_config, \
        with patch.object(self.executor, "_execute_oks_dump") as mock_exec, \
             patch("oksquery_translator.executor.logger.warning") as mock_warn:
            mock_exec_config.return_value = ExecutionResult(success=True, count=1)
            
            mock_exec.return_value = ExecutionResult(success=True, count=1)

            res = self.executor.execute(
                target_class="Application",
                query='(all ("InitTimeout" "30" >))',
                version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
                data_file="muons/partitions/part_TGC_FillTest.data.xml",
                release="tdaq-11-02-01",
            )
            self.assertTrue(res.success)
            self.assertTrue(mock_warn.called)
            warn_msg = str(mock_warn.call_args)
            self.assertIn("Active TDAQ release is 'tdaq-12-00-00'", warn_msg)
            self.assertIn("run specifies release 'tdaq-11-02-01'", warn_msg)

    @patch.dict(os.environ, {}, clear=True)
    def test_9_auto_derived_repository_url(self):
        """Test 9: Auto-derives Point-1 (p1) vs TestBed (tbed) repository URL based on release & partition with port 7999."""
        p1_url = self.executor._resolve_repository_url("tdaq-11-02-01", "part_TGC_FillTest")
        self.assertEqual(p1_url, "ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git")

        tbed_url = self.executor._resolve_repository_url("tdaq-11-02-01", "all_hosts")
        self.assertEqual(tbed_url, "ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/tbed/tdaq-11-02-01.git")

        # Verify historical release tdaq-11-02-00
        tdaq_11_02_00_url = self.executor._resolve_repository_url("tdaq-11-02-00", "part_TGC_FillTest")
        self.assertEqual(tdaq_11_02_00_url, "ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-00.git")

        # Verify normalization of explicit SSH URLs lacking port 7999
        normalized = self.executor._normalize_repository_url("ssh://git@gitlab.cern.ch/atlas-tdaq-oks/p1/tdaq-11-02-00.git")
        self.assertEqual(normalized, "ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-00.git")

        # Verify HTTPS URL preservation (port 7999 not added to HTTPS)
        https_url = self.executor._normalize_repository_url("https://gitlab.cern.ch/atlas-tdaq-oks/p1/tdaq-11-02-00.git")
        self.assertEqual(https_url, "https://gitlab.cern.ch/atlas-tdaq-oks/p1/tdaq-11-02-00.git")

    def test_10_metadata_repository_wins_over_environment_and_uses_ssh(self):
        """A recorded repository is never replaced by a current-release URL."""
        with patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "ssh://git@current/repo.git"}, clear=True):
            captured = {}

            def execute(*_args, **_kwargs):
                captured.update({
                    "repository": os.environ.get("TDAQ_DB_REPOSITORY"),
                    "protocol": os.environ.get("OKS_GIT_PROTOCOL"),
                    "user_repo": os.environ.get("TDAQ_DB_USER_REPOSITORY"),
                    "db_path": os.environ.get("TDAQ_DB_PATH"),
                })
            def execute_dump(*_args, **_kwargs):
                captured["repository"] = _kwargs.get("repository")
                return ExecutionResult(success=True)

            with patch.object(self.executor, "_execute_config", side_effect=execute):
            with patch.object(Executor, "_validate_historical_configuration", return_value=None), \
                 patch.object(self.executor, "_execute_oks_dump", side_effect=execute_dump):
                self.executor._oks_dump_path = "/fake/oks_dump"
                result = self.executor.execute(
                    "Application", '(all (object-id "" !=))',
                    version="tag:run-tag", release="tdaq-99-99-99",
                    partition="ATLAS", repository="ssh://git@recorded/history.git",
                    data_file="combined/partitions/ATLAS.data.xml",
                )
            self.assertTrue(result.success)
            # The recorded repository must take precedence over the env var.
            self.assertEqual(captured["repository"], "ssh://git@recorded/history.git")
            self.assertEqual(captured["protocol"], "ssh")
            self.assertIsNone(captured["user_repo"])
            self.assertIsNone(captured["db_path"])

    def test_11_git_preflight_accepts_tag_and_hash_and_checks_file(self):
        """Use a separate local Git repository to prove selection is revision-driven."""
        with tempfile.TemporaryDirectory() as temp_dir:
            work = os.path.join(temp_dir, "work")
            remote = os.path.join(temp_dir, "history.git")
            os.mkdir(work)
            def run(*cmd, cwd=work):
                return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
            run("git", "init", "--quiet")
            run("git", "config", "user.email", "test@example.invalid")
            run("git", "config", "user.name", "Test")
            os.makedirs(os.path.join(work, "one", "partitions"))
            path = os.path.join(work, "one", "partitions", "first.data.xml")
            with open(path, "w", encoding="utf-8") as stream:
                stream.write("<oks/>")
            run("git", "add", ".")
            run("git", "commit", "--quiet", "-m", "first")
            first_sha = run("git", "rev-parse", "HEAD").stdout.strip()
            run("git", "tag", "r1@first")
            run("git", "init", "--bare", "--quiet", remote, cwd=temp_dir)
            run("git", "remote", "add", "origin", remote)
            run("git", "push", "--quiet", "--tags", "origin", "HEAD")

            self.assertIsNone(Executor._validate_historical_configuration(
                remote, "tag:r1@first", "one/partitions/first.data.xml", "tdaq-01-00-00", "first"))
            self.assertIsNone(Executor._validate_historical_configuration(
                remote, "hash:" + first_sha, "one/partitions/first.data.xml", "tdaq-01-00-00", "first"))
            error = Executor._validate_historical_configuration(
                remote, "tag:r1@first", "missing.data.xml", "tdaq-01-00-00", "first")
            self.assertIn("data-file resolution failed", error)

    @patch.dict(os.environ, {"TDAQ_DB_REPOSITORY": "ssh://git@gitlab.cern.ch:7999/atlas-tdaq-oks/p1/tdaq-11-02-01.git"}, clear=True)
    @patch("subprocess.run")
    def test_13_missing_shared_library_fallback_to_host_oks_dump(self, mock_run):
        """Test 13: Automatically fall back to host oks_dump if release binary fails with exit 127 / missing shared library error (e.g. libssl.so.10)."""
        call_count = 0

        def side_effect(cmd, **_kwargs):
            nonlocal call_count
            call_count += 1
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "/cvmfs/" in cmd_str:
                return MagicMock(
                    returncode=127,
                    stdout="",
                    stderr="oks_dump: error while loading shared libraries: libssl.so.10: cannot open shared object file: No such file or directory"
                )
            return MagicMock(
                returncode=0,
                stdout='Object "app1@Application"\n  InitTimeout: 40\n',
                stderr=""
            )

        mock_run.side_effect = side_effect
        self.executor._oks_dump_path = "/usr/bin/oks_dump"

        res = self.executor._execute_oks_dump(
            target_class="Application",
            query='(all ("InitTimeout" "30" >))',
            max_objects=10,
            version_label="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            data_file="muons/partitions/part_TGC_FillTest.data.xml",
            oks_dump_path="/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-11-02-01/installed/x86_64-centos7-gcc11-dbg/bin/oks_dump",
            version="hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
        )
        self.assertTrue(res.success, res.message)
        self.assertEqual(res.count, 1)
        self.assertGreaterEqual(call_count, 2)


if __name__ == "__main__":
    unittest.main()
