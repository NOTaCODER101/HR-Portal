from config.database import db
from datetime import datetime, timezone

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    employees = db.relationship('Employee', back_populates='department')

    def __repr__(self):
        return f"<Department {self.name}>"
