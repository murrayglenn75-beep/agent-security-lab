"""Offline reference monitor for synthetic agent messaging and egress proposals.

This example does not inspect or enforce operating-system network calls.
An independent execution broker must enforce the policy for real effects.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ChannelRequest:
    actor: str
    tenant: str
    destination: str
    operation: str

@dataclass(frozen=True)
class ScopedGrant:
    actor: str
    tenant: str
    allowed_destinations: frozenset[str]
    allowed_operations: frozenset[str]
    approved: bool

def authorize(request: ChannelRequest, grant: ScopedGrant | None) -> bool:
    if grant is None or not grant.approved:
        return False
    if not request.actor or not request.tenant or not request.destination or not request.operation:
        return False
    return (
        request.actor == grant.actor
        and request.tenant == grant.tenant
        and request.destination in grant.allowed_destinations
        and request.operation in grant.allowed_operations
    )
