"""
services/audit_service.py
=========================
Centralised audit trail service.

All other services call `AuditService.log_activity()` after every significant
state change (create, update, delete, approve, login, logout) so HR Admins
can trace exactly who did what and when. This service intentionally does NOT
commit — commits happen in the calling service's transaction boundary.
"""
from typing import Optional
from dao.audit_log_dao import AuditLogDAO


class AuditService:
    """Thin wrapper around AuditLogDAO for cross-service audit logging."""

    def __init__(self) -> None:
        self._dao = AuditLogDAO()

    def log_activity(
        self,
        user_id: Optional[int],
        action: str,
        entity: str,
        entity_id: Optional[int] = None,
        details: Optional[str] = None,
    ) -> None:
        """
        Record an audit trail entry.

        Args:
            user_id:   ID of the user who performed the action (None for system events).
            action:    Short verb describing the action, e.g. 'LOGIN', 'APPROVE_LEAVE'.
            entity:    The model/table involved, e.g. 'LeaveRequest', 'Employee'.
            entity_id: Primary key of the affected record (optional).
            details:   Free-text JSON or description for extra context (optional).
        """
        self._dao.log_action(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
        )
