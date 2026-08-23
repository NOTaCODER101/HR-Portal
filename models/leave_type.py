from config.database import db

class LeaveType(db.Model):
    __tablename__ = 'leave_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., Annual, Sick, Casual
    default_days = db.Column(db.Integer, nullable=False) # Default days given per year
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<LeaveType {self.name}>"
