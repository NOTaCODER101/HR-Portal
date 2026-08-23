from config.database import db
from datetime import datetime, timezone

class Designation(db.Model):
    __tablename__ = 'designations'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    employees = db.relationship('Employee', back_populates='designation')

    def __repr__(self):
        return f"<Designation {self.title}>"
