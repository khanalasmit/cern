"""Subprocess adapter for the native ``oks_dump`` executable."""

from dataclasses import dataclass
from pathlib import Path
import subprocess

from .context import HistoricalExecutionContext


class OksDumpError(RuntimeError):
    """Raised when ``oks_dump`` cannot execute a historical query."""


@dataclass(frozen=True)
class OksDumpResult:
    revision: str
    target_class: str
    command: tuple[str, ...]
    stdout: str
    stderr: str
    returncode: int


class OksDumpExecutor:
    """Execute a historical query through the native OKS CLI.

    ``oks_dump`` returns human-readable output, so this adapter deliberately
    returns raw stdout. Result normalization belongs in a later layer once the
    exact OKS output format and deployment version are confirmed.
    """

    EXIT_CODE_MEANINGS = {
        1: "bad command line",
        2: "bad OKS file(s)",
        3: "bad query",
        4: "class not found",
        5: "dangling references found",
    }

    def __init__(self, executable: str = "oks_dump", timeout: float = 60.0):
        self.executable = executable
        self.timeout = timeout

    def execute(self, context: HistoricalExecutionContext) -> OksDumpResult:
        target_class = context.require_target_class()
        snapshot = context.snapshot
        if snapshot.source is None:
            raise OksDumpError(
                "oks_dump execution requires a source-backed snapshot"
            )

        with snapshot.source.materialize() as root:
            data_files = tuple(
                str((Path(root) / relative_path).resolve())
                for relative_path in snapshot.data_paths
            )
            command = (
                self.executable,
                "--class",
                target_class,
                "--query",
                context.oks_query,
                *data_files,
            )
            try:
                completed = subprocess.run(
                    list(command),
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout,
                )
            except FileNotFoundError as exc:
                raise OksDumpError(
                    f"OKS executable was not found: {self.executable!r}"
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise OksDumpError(
                    f"oks_dump exceeded timeout of {self.timeout} seconds"
                ) from exc
            except OSError as exc:
                raise OksDumpError(f"could not start oks_dump: {exc}") from exc

        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        result = OksDumpResult(
            revision=snapshot.revision.commit,
            target_class=target_class,
            command=command,
            stdout=stdout,
            stderr=stderr,
            returncode=completed.returncode,
        )
        if completed.returncode != 0:
            meaning = self.EXIT_CODE_MEANINGS.get(
                completed.returncode,
                "unknown oks_dump failure",
            )
            raise OksDumpError(
                f"oks_dump failed with exit code {completed.returncode} "
                f"({meaning}) for revision {result.revision}: {stderr.strip()}"
            )
        return result
