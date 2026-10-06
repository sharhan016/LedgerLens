import uuid
from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    COMPLIANCE = "compliance"
    ADMIN = "admin"


class Permission(StrEnum):
    DOCUMENTS_READ = "documents:read"
    DOCUMENTS_WRITE = "documents:write"
    AUDIT_READ = "audit:read"
    OPERATIONS_READ = "operations:read"
    USERS_MANAGE = "users:manage"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.VIEWER: frozenset({Permission.DOCUMENTS_READ}),
    Role.ANALYST: frozenset({Permission.DOCUMENTS_READ}),
    Role.COMPLIANCE: frozenset(
        {Permission.DOCUMENTS_READ, Permission.DOCUMENTS_WRITE, Permission.AUDIT_READ}
    ),
    Role.ADMIN: frozenset(Permission),
}


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: Role

    def can(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS[self.role]
