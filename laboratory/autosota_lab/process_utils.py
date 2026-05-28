from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
from typing import Mapping


def run_process(
    args: list[str],
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout_seconds: int | None = None,
    stream_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    if not stream_output:
        return subprocess.run(
            args,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )

    proc = subprocess.Popen(
        args,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
    )
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    def pump(stream, chunks: list[str], target) -> None:
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            chunks.append(line)
            target.write(line)
            target.flush()
        stream.close()

    stdout_thread = threading.Thread(target=pump, args=(proc.stdout, stdout_chunks, sys.stdout), daemon=True)
    stderr_thread = threading.Thread(target=pump, args=(proc.stderr, stderr_chunks, sys.stderr), daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    try:
        returncode = proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        proc.kill()
        returncode = proc.wait()
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        stdout = "".join(stdout_chunks)
        stderr = "".join(stderr_chunks)
        raise subprocess.TimeoutExpired(exc.cmd, exc.timeout, output=stdout, stderr=stderr) from exc

    stdout_thread.join()
    stderr_thread.join()
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout="".join(stdout_chunks),
        stderr="".join(stderr_chunks),
    )
