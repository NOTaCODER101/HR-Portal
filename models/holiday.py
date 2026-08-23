from config.database import db

class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Holiday {self.name} on {self.date}>"
