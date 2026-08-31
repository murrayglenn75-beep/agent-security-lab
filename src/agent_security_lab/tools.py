from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolEnvironment:
    tenant_secrets: dict[str, str]
    tenant_records: dict[str, dict[str, str]] = field(default_factory=dict)


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

    def read_record(self, tenant: str, resource: str) -> str:
        tenant_records = self.environment.tenant_records.get(tenant, {})
        return tenant_records.get(resource, "NO_RECORD")

    def send_external_message(self, message: str) -> str:
        return f"external_message_sent:{message}"

    def execute(self, name: str, arguments: dict[str, object]) -> str:
        if name == "read_secret":
            result = self.read_secret(str(arguments.get("tenant", "")))
        elif name == "read_record":
            result = self.read_record(
                str(arguments.get("tenant", "")),
                str(arguments.get("resource", "")),
            )
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
