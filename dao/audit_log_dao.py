from typing import List, Optional
from sqlalchemy.orm import joinedload
from config.database import db
from models.audit_log import AuditLog
from dao.base_dao import BaseDAO

class AuditLogDAO(BaseDAO):
    def __init__(self):
        super().__init__(AuditLog)

    def log_action(self, user_id: Optional[int], action: str, entity: str, entity_id: Optional[int] = None, details: Optional[str] = None) -> AuditLog:
        """Create a new system audit log."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details
        )
        self.add(log)
        return log

    def get_recent_logs(self, offset: int = 0, limit: int = 100) -> List[AuditLog]:
        """Fetch paginated audit logs, eager loading the user who performed the action."""
        return db.session.query(AuditLog)\
            .options(joinedload(AuditLog.user))\
            .order_by(AuditLog.timestamp.desc())\
            .offset(offset).limit(limit).all()
