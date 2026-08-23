from config.database import db

class LeaveBalance(db.Model):
    __tablename__ = 'leave_balances'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    allocated_days = db.Column(db.Integer, nullable=False)
    used_days = db.Column(db.Float, default=0.0, nullable=False)

    # Relationships
    employee = db.relationship('Employee', backref=db.backref('leave_balances', lazy=True))
    leave_type = db.relationship('LeaveType')

    def __repr__(self):
        return f"<LeaveBalance Employee:{self.employee_id} Type:{self.leave_type_id} Year:{self.year}>"
