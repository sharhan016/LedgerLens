import uuid

from app.security.principal import Role

DEMO_TENANT_ID = uuid.uuid5(uuid.NAMESPACE_DNS, "northstar-union-bank.demo")
DEMO_TENANT_NAME = "Northstar Union Bank · Synthetic"
DEMO_USERS = {
    Role.ANALYST: (
        uuid.uuid5(uuid.NAMESPACE_DNS, "analyst@northstar.demo"),
        "analyst@northstar.demo",
        "Asha Rao",
    ),
    Role.COMPLIANCE: (
        uuid.uuid5(uuid.NAMESPACE_DNS, "compliance@northstar.demo"),
        "compliance@northstar.demo",
        "Mira Fernandes",
    ),
    Role.ADMIN: (
        uuid.uuid5(uuid.NAMESPACE_DNS, "admin@northstar.demo"),
        "admin@northstar.demo",
        "Dev Malhotra",
    ),
}
