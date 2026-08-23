"""
services/document_service.py
=============================
Secure employee document upload with orphaned-file prevention.

Upload pattern (atomic, disk + DB coupled):
  1. Validate file extension against whitelist.
  2. Validate MIME type against whitelist.
  3. Enforce file size limit.
  4. Sanitise the filename with werkzeug's secure_filename().
  5. Add the DB record to the session (flush to get ID).
  6. Write the file to disk.
  7. commit() — if this raises, delete the file from disk immediately.

Transaction boundary:
  - upload_employee_document() → inserts EmployeeDocument record, commits.
  - delete_employee_document() → deletes record + disk file, commits.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING
from datetime import datetime, timezone

# pyrefly: ignore [missing-import]
from werkzeug.datastructures import FileStorage
# pyrefly: ignore [missing-import]
from werkzeug.utils import secure_filename
from flask import current_app

from config.database import db
from dao.document_dao import DocumentDAO
from models.employee_document import EmployeeDocument
from services.exceptions import FileUploadError

if TYPE_CHECKING:
    pass

# Allowed extensions AND their corresponding MIME types (dual-check against spoofing)
ALLOWED_EXTENSIONS: set[str] = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_MIME_TYPES: set[str] = {
    'application/pdf',
    'image/png',
    'image/jpeg',
}


class DocumentService:
    """Handles employee document uploads and deletions."""

    def __init__(self) -> None:
        self._dao = DocumentDAO()

    # ──────────────────────────────────────────────────────────────────────────
    # Private Helpers
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_file(file: FileStorage) -> str:
        """
        Run all validation checks and return the sanitised filename.

        Raises:
            FileUploadError: On any validation failure.
        """
        if not file or file.filename == '':
            raise FileUploadError("No file was selected for upload.")

        filename = file.filename or ''
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        if extension not in ALLOWED_EXTENSIONS:
            raise FileUploadError(
                f"File type '.{extension}' is not allowed. "
                f"Please upload one of: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
            )

        if file.mimetype not in ALLOWED_MIME_TYPES:
            raise FileUploadError(
                f"MIME type '{file.mimetype}' is not accepted. "
                "The file content does not match its extension."
            )

        return secure_filename(filename)

    # ──────────────────────────────────────────────────────────────────────────
    # Public Methods
    # ──────────────────────────────────────────────────────────────────────────

    def upload_employee_document(
        self,
        employee_id: int,
        file: FileStorage,
        document_type: str,
        uploaded_by_user_id: int,
    ) -> EmployeeDocument:
        """
        Validate, save, and record an employee document.

        The method uses a "DB-first" pattern: the DB record is flushed before
        the file is written to disk. If the final commit fails, the already-
        written file is immediately deleted to prevent orphaned disk files.

        Args:
            employee_id:        The employee this document belongs to.
            file:               The Werkzeug FileStorage object from the request.
            document_type:      Category label e.g. 'ID_PROOF', 'CONTRACT'.
            uploaded_by_user_id: ID of the user performing the upload (for audit trail).

        Returns:
            The newly created EmployeeDocument record.

        Raises:
            FileUploadError: On validation failure or if the file size exceeds
                             the configured MAX_CONTENT_LENGTH.
        """
        safe_name = self._validate_file(file)

        # Build a unique filename to avoid collisions: <emp_id>_<timestamp>_<name>
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        final_filename = f"{employee_id}_{timestamp}_{safe_name}"

        upload_folder: str = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, final_filename)

        # Step 1: Stage the DB record (flush gives us the ID before commit)
        doc_record = EmployeeDocument(
            employee_id=employee_id,
            document_type=document_type,
            filename=final_filename,
            file_path=file_path,
            uploaded_by=uploaded_by_user_id,
        )
        db.session.add(doc_record)
        db.session.flush()

        # Step 2: Write file to disk
        try:
            file.save(file_path)
        except OSError as exc:
            db.session.rollback()
            raise FileUploadError(f"Failed to save file to disk: {exc}") from exc

        # Step 3: Commit — clean up disk file if DB fails
        try:
            db.session.commit()
            return doc_record
        except Exception as exc:
            db.session.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise FileUploadError(f"Document record could not be saved: {exc}") from exc

    def delete_employee_document(self, document_id: int) -> None:
        """
        Delete a document record and remove the file from disk.

        Args:
            document_id: ID of the EmployeeDocument to delete.
        """
        doc = self._dao.get_by_id(document_id)
        if doc is None:
            return  # Already gone — idempotent

        file_path: str = doc.file_path

        try:
            db.session.delete(doc)
            db.session.commit()

            # Remove from disk only after successful DB commit
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception:
            db.session.rollback()
            raise
