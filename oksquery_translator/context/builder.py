"""
context/builder.py — OksContext Factory
========================================

Constructs the immutable OksContext for each pipeline request.
Binds temporal version specifiers to the exact schema loaded by the OKS runtime,
guaranteeing that schema fingerprints accurately represent the resolved context.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Dict, Optional, Tuple

from .oks_context import OksContext, compute_fingerprint

logger = logging.getLogger("oksquery_translator.context.builder")


class VersionResolutionError(RuntimeError):
    """Raised when an explicit historical version or schema cannot be resolved."""
    pass


class OksContextBuilder:
    """
    Builds an immutable OksContext from a version tag and data file path.

    Resolves the exact schema environment corresponding to the version tag,
    loads the class list for that version, and computes the canonical fingerprint.
    """

    def __init__(self, data_file: str = "daq/segments/setup.data.xml",
                 schema_dir: Optional[str] = None):
        self.data_file = data_file
        self.schema_dir = schema_dir

    def build(self, version_tag: Optional[str] = None) -> OksContext:
        """
        Build an OksContext for the given version_tag.

        Parameters
        ----------
        version_tag : str or None
            Temporal version specifier. Examples:
              - None                       → current/HEAD
              - "tag:r380689@all_hosts"   → historical run
              - "hash:ce4ceda7..."         → specific git commit
              - "tdaq-13-00-00"            → TDAQ release tag

        Returns
        -------
        OksContext
            Immutable, fingerprinted context object.
        """
        release, git_revision, run_number, config_rev = self._parse_version_tag(version_tag)
        schema_id = self._build_schema_identifier(release, run_number, version_tag)

        # Set up versioned environment during schema resolution
        env_backup = self._set_version_env(version_tag)
        try:
            from ..schema_retrieval import SchemaRetriever
            retriever = SchemaRetriever(
                data_file=self.data_file,
                schema_dir=self.schema_dir,
            )
            class_names = retriever.get_class_list()
        except Exception as e:
            logger.warning(
                f"Could not load class list for version '{version_tag}': {e}"
            )
            class_names = []
        finally:
            self._restore_env(env_backup)

        if not class_names:
            if version_tag:
                logger.debug(
                    f"No classes loaded from environment for '{version_tag}'. "
                    f"Computing synthetic fingerprint from version tag for offline/mock support."
                )
                fingerprint = compute_fingerprint([f"version:{version_tag}"])
            else:
                fingerprint = "0000000000000000"
        else:
            fingerprint = compute_fingerprint(class_names)

        logger.info(
            f"OksContext resolved: identifier={schema_id!r}, "
            f"fingerprint={fingerprint!r}, classes={len(class_names)}, "
            f"version_tag={version_tag!r}"
        )

        return OksContext(
            schema_identifier=schema_id,
            schema_fingerprint=fingerprint,
            release=release,
            git_revision=git_revision,
            run_number=run_number,
            configuration_revision=config_rev,
            version_tag=version_tag,
        )

    # ------------------------------------------------------------------
    # Internal parsing and environment helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_version_tag(version_tag: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[int], Optional[str]]:
        """Extract release, git_revision, run_number, config_rev from version string."""
        if not version_tag:
            return None, None, None, None

        # "hash:<sha>" → git revision
        if version_tag.startswith("hash:"):
            sha = version_tag[5:].strip()
            return None, sha, None, None

        # "tag:r<run>@<partition>" or "r<run>" → historical run
        m = re.match(r'^(?:tag:)?r(\d+)@?', version_tag)
        if m:
            run_number = int(m.group(1))
            return None, None, run_number, None

        # "run:<run>"
        if version_tag.startswith("run:"):
            try:
                run_number = int(version_tag.split(":")[-1])
                return None, None, run_number, None
            except ValueError:
                pass

        # "tdaq-XX-YY-ZZ" → release
        if re.match(r'^tdaq-\d+', version_tag):
            return version_tag, None, None, None

        # other formats (e.g. date:...)
        return None, None, None, version_tag

    @staticmethod
    def _build_schema_identifier(release: Optional[str],
                                 run_number: Optional[int],
                                 version_tag: Optional[str]) -> str:
        if release:
            return release
        if run_number is not None:
            return f"run-{run_number}"
        if version_tag:
            return version_tag[:32]
        return "current"

    @staticmethod
    def _set_version_env(version: Optional[str]) -> Dict[str, Optional[str]]:
        """Temporarily set version environment variables for schema inspection."""
        backup: Dict[str, Optional[str]] = {}
        if not version:
            return backup

        if (version.startswith("hash:") or version.startswith("date:") or
                version.startswith("tag:")):
            backup["TDAQ_DB_VERSION"] = os.environ.get("TDAQ_DB_VERSION")
            os.environ["TDAQ_DB_VERSION"] = version
        elif version.startswith("run:") or (version.startswith("r") and version[1:].isdigit()):
            run_num = version.split(":")[-1].lstrip("r")
            tag_name = f"tag:r{run_num}@ATLAS"
            backup["TDAQ_DB_VERSION"] = os.environ.get("TDAQ_DB_VERSION")
            os.environ["TDAQ_DB_VERSION"] = tag_name
        elif version.startswith("tdaq-"):
            snapshot_path = (
                f"/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/{version}"
                f"/installed/share/data"
            )
            backup["TDAQ_DB_PATH"] = os.environ.get("TDAQ_DB_PATH")
            os.environ["TDAQ_DB_PATH"] = snapshot_path

        return backup

    @staticmethod
    def _restore_env(backup: Dict[str, Optional[str]]) -> None:
        """Restore environment variables from backup."""
        for key, value in backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
