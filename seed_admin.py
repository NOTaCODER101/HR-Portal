"""
seed_admin.py
=============
One-time script to create the first HR Admin user.
Run this ONCE after `init_db.py` to create your initial login.

Usage:
    .venv\\Scripts\\python.exe seed_admin.py
"""
from app import create_app
from config.database import db
from models.user import User
from models.employee import Employee
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():
    # Check if admin already exists
    existing = User.query.filter_by(username='admin').first()
    if existing:
        print("[OK] Admin user already exists. Username: 'admin'")
    else:
        # Create the HR Admin user account
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('Admin@HR2024'),
            role='HR Admin',
            is_active=True,
        )
        db.session.add(admin_user)
        db.session.flush()  # get admin_user.id

        # Create a minimal Employee record linked to the admin user
        admin_employee = Employee(
            user_id=admin_user.id,
            first_name='HR',
            last_name='Administrator',
            email='admin@hrportal.com',
            date_of_joining=date.today(),
        )
        db.session.add(admin_employee)
        db.session.commit()

        print("[OK] Admin user created successfully!")
        print("-" * 40)
        print("  Username : admin")
        print("  Password : Admin@HR2024")
        print("  Role     : HR Admin")
        print("-" * 40)
        print("[!] Change the password after your first login!")
