import uuid
from collections.abc import Sequence

from app.repositories.documents import DocumentRecord, DocumentRepository
from app.security.principal import Permission, Principal


class PermissionDeniedError(RuntimeError):
    pass


class DocumentService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    @staticmethod
    def _authorize(principal: Principal) -> None:
        if not principal.can(Permission.DOCUMENTS_READ):
            raise PermissionDeniedError("documents:read permission required")

    async def list_documents(self, principal: Principal) -> Sequence[DocumentRecord]:
        self._authorize(principal)
        return await self._repository.list_visible(principal.tenant_id, principal.role)

    async def get_document(
        self, principal: Principal, document_id: uuid.UUID
    ) -> DocumentRecord | None:
        self._authorize(principal)
        return await self._repository.get_visible(principal.tenant_id, principal.role, document_id)

