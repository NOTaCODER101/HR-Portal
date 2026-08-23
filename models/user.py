from config.database import db
from datetime import datetime, timezone

class User(db.Model):
    """
    Represents a system login account.
    Decoupled from Flask-Login — authentication is handled by Flask-JWT-Extended.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Employee')  # Employee | Manager | HR Admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    employee = db.relationship('Employee', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username} (Role: {self.role}, Active: {self.is_active})>"
