from config.database import db
from datetime import datetime, timezone

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable for system actions
    action = db.Column(db.String(100), nullable=False)
    entity = db.Column(db.String(50), nullable=False) # e.g., Employee, LeaveRequest
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User')

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity}>"
