"""Unit tests for the Document aggregate."""

import pytest

from src.domain.document.document import ALLOWED_FILE_TYPES, MAX_FILE_SIZE, Document
from src.domain.document.errors import FileTooLargeError, InvalidFileTypeError
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.user.user import UserId


def _make_document(
    file_type: str = "application/pdf",
    file_size_bytes: int = 1024,
    project_id: ProjectId | None = None,
) -> Document:
    return Document.create(
        org_id=OrganizationId.generate(),
        project_id=project_id,
        uploaded_by=UserId("user-123"),
        filename="test.pdf",
        file_type=file_type,
        file_size_bytes=file_size_bytes,
        storage_path="/uploads/test.pdf",
    )


class TestDocumentCreate:
    def test_creates_document_with_valid_pdf(self):
        doc = _make_document()
        assert doc.id is not None
        assert doc.filename == "test.pdf"
        assert doc.file_type == "application/pdf"
        assert doc.file_size_bytes == 1024

    def test_creates_document_without_project(self):
        doc = _make_document(project_id=None)
        assert doc.project_id is None

    def test_creates_document_with_project(self):
        pid = ProjectId.generate()
        doc = _make_document(project_id=pid)
        assert doc.project_id == pid

    def test_raises_file_too_large(self):
        with pytest.raises(FileTooLargeError):
            _make_document(file_size_bytes=MAX_FILE_SIZE + 1)

    def test_allows_exact_max_size(self):
        doc = _make_document(file_size_bytes=MAX_FILE_SIZE)
        assert doc.file_size_bytes == MAX_FILE_SIZE

    def test_raises_invalid_file_type(self):
        with pytest.raises(InvalidFileTypeError):
            _make_document(file_type="application/x-executable")

    @pytest.mark.parametrize("file_type", sorted(ALLOWED_FILE_TYPES))
    def test_allows_all_valid_file_types(self, file_type: str):
        doc = _make_document(file_type=file_type)
        assert doc.file_type == file_type

    def test_generates_unique_ids(self):
        doc1 = _make_document()
        doc2 = _make_document()
        assert doc1.id != doc2.id

    def test_created_at_is_set(self):
        doc = _make_document()
        assert doc.created_at is not None
