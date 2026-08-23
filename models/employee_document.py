from config.database import db
from datetime import datetime, timezone

class EmployeeDocument(db.Model):
    __tablename__ = 'employee_documents'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False) # e.g., ID Proof, Certificate, Resume
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    employee = db.relationship('Employee', backref=db.backref('documents', lazy=True))
    uploader = db.relationship('User', foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<EmployeeDocument {self.document_type} for Employee {self.employee_id}>"
