from .docker_runner import DockerRunner
from .code_agent import CodeAgentRunner


class ClaudeCodeRunner(CodeAgentRunner):
    """Backward-compatible Claude Code runner."""

    def __init__(self, docker: DockerRunner, claude_command: str = "claude") -> None:
        super().__init__(runner=docker, agent="claude", command=claude_command)
