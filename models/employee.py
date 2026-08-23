from config.database import db
from datetime import datetime, timezone

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    date_of_joining = db.Column(db.Date, nullable=False)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designations.id'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='employee')
    department = db.relationship('Department', back_populates='employees')
    designation = db.relationship('Designation', back_populates='employees')
    manager = db.relationship('Employee', remote_side=[id], backref='team_members')

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name}>"
