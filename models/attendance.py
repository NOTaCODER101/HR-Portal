from config.database import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time, nullable=True)
    check_out = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Present') # Present, Absent, Half Day
    notes = db.Column(db.String(255), nullable=True)

    # Relationships
    employee = db.relationship('Employee', backref=db.backref('attendances', lazy=True))

    @property
    def check_in_time(self):
        if self.check_in is not None and self.date:
            from datetime import timedelta
            if isinstance(self.check_in, timedelta):
                return datetime.combine(self.date, datetime.min.time()) + self.check_in
            else:
                return datetime.combine(self.date, self.check_in)
        return None

    @property
    def check_out_time(self):
        if self.check_out is not None and self.date:
            from datetime import timedelta
            if isinstance(self.check_out, timedelta):
                return datetime.combine(self.date, datetime.min.time()) + self.check_out
            else:
                return datetime.combine(self.date, self.check_out)
        return None

    def __repr__(self):
        return f"<Attendance {self.date} for Employee {self.employee_id}>"
