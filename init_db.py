from app import create_app
from config.database import db

# We need to import all models before calling create_all
# so that SQLAlchemy knows about them.
import models

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")

