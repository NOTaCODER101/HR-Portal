"""
seed_data.py
============
Seeds departments, designations, and leave types into the database.
Run once after init_db.py: python seed_data.py
"""
from app import create_app
from config.database import db
from models.department import Department
from models.designation import Designation
from models.leave_type import LeaveType

DEPARTMENTS = [
    "Engineering", "Human Resources", "Finance", "Marketing",
    "Sales", "Operations", "Legal", "Customer Support", "Product Management"
]

DESIGNATIONS = [
    "Software Engineer", "Senior Software Engineer", "Lead Engineer",
    "HR Manager", "HR Executive", "Finance Manager", "Accountant",
    "Marketing Manager", "Sales Executive", "Operations Manager",
    "Product Manager", "Customer Support Executive", "Legal Counsel",
    "Director", "Vice President", "Chief Executive Officer"
]

LEAVE_TYPES = [
    {"name": "Annual Leave",    "default_days": 21},
    {"name": "Sick Leave",      "default_days": 10},
    {"name": "Casual Leave",    "default_days": 7},
    {"name": "Maternity Leave", "default_days": 90},
    {"name": "Paternity Leave", "default_days": 15},
    {"name": "Unpaid Leave",    "default_days": 30},
]

def seed():
    app = create_app()
    with app.app_context():
        seeded = False

        # ── Departments ────────────────────────────────────────────────────────
        if Department.query.count() == 0:
            for name in DEPARTMENTS:
                db.session.add(Department(name=name))
            print(f"[OK] Seeded {len(DEPARTMENTS)} departments.")
            seeded = True
        else:
            print(f"[--] Departments already exist ({Department.query.count()} found), skipping.")

        # ── Designations ───────────────────────────────────────────────────────
        if Designation.query.count() == 0:
            for title in DESIGNATIONS:
                db.session.add(Designation(title=title))
            print(f"[OK] Seeded {len(DESIGNATIONS)} designations.")
            seeded = True
        else:
            print(f"[--] Designations already exist ({Designation.query.count()} found), skipping.")

        # ── Leave Types ────────────────────────────────────────────────────────
        if LeaveType.query.count() == 0:
            for lt in LEAVE_TYPES:
                db.session.add(LeaveType(name=lt["name"], default_days=lt["default_days"]))
            print(f"[OK] Seeded {len(LEAVE_TYPES)} leave types.")
            seeded = True
        else:
            print(f"[--] Leave types already exist ({LeaveType.query.count()} found), skipping.")

        if seeded:
            db.session.commit()
            print("\n[OK] Seed data committed successfully!")
        else:
            print("\n[--] Nothing to seed — all data already present.")

if __name__ == "__main__":
    seed()
