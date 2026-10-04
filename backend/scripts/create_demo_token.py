import argparse
import uuid

from app.core.config import get_settings
from app.security.principal import Principal, Role
from app.security.tokens import TokenService


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local LedgerLens demo access token")
    parser.add_argument("--user-id", type=uuid.UUID, required=True)
    parser.add_argument("--tenant-id", type=uuid.UUID, required=True)
    parser.add_argument("--role", type=Role, choices=list(Role), required=True)
    args = parser.parse_args()
    principal = Principal(user_id=args.user_id, tenant_id=args.tenant_id, role=args.role)
    print(TokenService(get_settings()).issue(principal))


if __name__ == "__main__":
    main()

