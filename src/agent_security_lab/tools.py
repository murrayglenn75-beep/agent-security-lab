from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolEnvironment:
    tenant_secrets: dict[str, str]


@dataclass(frozen=True)
class ToolExecution:
    name: str
    arguments: dict[str, object]
    result: str
    side_effect: bool


class ToolSimulator:
    def __init__(self, environment: ToolEnvironment) -> None:
        self.environment = environment
        self.execution_log: list[ToolExecution] = []

    def read_secret(self, tenant: str) -> str:
        return self.environment.tenant_secrets.get(tenant, "NO_SECRET")

    def send_external_message(self, message: str) -> str:
        return f"external_message_sent:{message}"

    def execute(self, name: str, arguments: dict[str, object]) -> str:
        if name == "read_secret":
            result = self.read_secret(str(arguments.get("tenant", "")))
        elif name == "send_external_message":
            result = self.send_external_message(str(arguments.get("message", "")))
        else:
            result = f"unknown_tool:{name}"

        self.execution_log.append(
            ToolExecution(
                name=name,
                arguments=dict(arguments),
                result=result,
                side_effect=name == "send_external_message",
            )
        )
        return result
