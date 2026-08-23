"""
services/employee_service.py
============================
Employee lifecycle management — onboarding, offboarding, and dashboard data aggregation.

Transaction boundary:
  - onboard_employee()  → creates User + Employee atomically in one commit.
  - offboard_employee() → deactivates User, commits.
  - get_employee_dashboard_data() → read-only, no commit needed.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from werkzeug.security import generate_password_hash

from config.database import db
from dao.attendance_dao import AttendanceDAO
from dao.employee_dao import EmployeeDAO
from dao.leave_dao import LeaveRequestDAO
from dao.user_dao import UserDAO
from models.employee import Employee
from models.user import User
from models.leave_type import LeaveType
from models.leave_balance import LeaveBalance
from services.audit_service import AuditService
from services.exceptions import DuplicateUsernameError, EmployeeNotFoundError


class EmployeeService:
    """Handles all employee lifecycle operations."""

    def __init__(self) -> None:
        self._user_dao = UserDAO()
        self._employee_dao = EmployeeDAO()
        self._attendance_dao = AttendanceDAO()
        self._leave_dao = LeaveRequestDAO()
        self._audit = AuditService()

    # ──────────────────────────────────────────────────────────────────────────
    # Public Methods
    # ──────────────────────────────────────────────────────────────────────────

    def onboard_employee(self, data: dict[str, Any], admin_user_id: int) -> Employee:
        """
        Atomically create a User login account and linked Employee profile.

        Expected keys in data:
            username, role, first_name, last_name, email, phone_number (opt),
            date_of_birth (opt), date_of_joining, department_id (opt),
            designation_id (opt), manager_id (opt).

        A default password of '<username>@HR2024' is set and must be changed
        on first login.

        Args:
            data:          Dictionary of employee + user fields.
            admin_user_id: ID of the HR Admin performing the action (for audit).

        Returns:
            The newly created Employee instance.

        Raises:
            DuplicateUsernameError: If the username already exists.
        """
        username: str = data['username']

        # Guard: check username uniqueness before inserting anything
        if self._user_dao.get_by_username(username) is not None:
            raise DuplicateUsernameError(username)

        default_password = f"{username}@HR2024"

        try:
            # Step 1 — Create User
            new_user = User(
                username=username,
                password_hash=generate_password_hash(default_password),
                role=data.get('role', 'Employee'),
                is_active=True,
            )
            db.session.add(new_user)
            db.session.flush()  # Assigns new_user.id without committing

            # Step 2 — Create Employee linked to the User
            new_employee = Employee(
                user_id=new_user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_number=data.get('phone_number'),
                gender=data.get('gender'),
                date_of_birth=data.get('date_of_birth'),
                date_of_joining=data.get('date_of_joining', date.today()),
                department_id=data.get('department_id'),
                designation_id=data.get('designation_id'),
                manager_id=data.get('manager_id'),
            )
            db.session.add(new_employee)
            db.session.flush()  # Assigns new_employee.id
            
            # Step 2.5 — Initialize Leave Balances
            current_year = date.today().year
            leave_types = LeaveType.query.all()
            for lt in leave_types:
                # Filter gender-specific leave types
                if lt.name == 'Maternity Leave' and new_employee.gender != 'Female':
                    continue
                if lt.name == 'Paternity Leave' and new_employee.gender != 'Male':
                    continue
                
                new_balance = LeaveBalance(
                    employee_id=new_employee.id,
                    leave_type_id=lt.id,
                    year=current_year,
                    allocated_days=lt.default_days,
                    used_days=0.0
                )
                db.session.add(new_balance)

            # Step 3 — Audit log (within same transaction)
            self._audit.log_activity(
                user_id=admin_user_id,
                action="ONBOARD_EMPLOYEE",
                entity="Employee",
                entity_id=new_employee.id,
                details=f"Employee '{data['first_name']} {data['last_name']}' onboarded with username '{username}'.",
            )

            db.session.commit()
            return new_employee

        except Exception:
            db.session.rollback()
            raise

    def offboard_employee(self, employee_id: int, admin_user_id: int) -> None:
        """
        Deactivate an employee's user account (soft delete / offboarding).

        Sets User.is_active = False so the employee can no longer log in.
        Does NOT delete any records to preserve historical audit data.

        Args:
            employee_id:   ID of the Employee record to offboard.
            admin_user_id: ID of the HR Admin performing the action (for audit).

        Raises:
            EmployeeNotFoundError: If no employee exists with the given ID.
        """
        employee = self._employee_dao.get_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFoundError(employee_id)

        try:
            self._user_dao.set_active_status(employee.user_id, is_active=False)
            employee.updated_at = datetime.now(timezone.utc)

            self._audit.log_activity(
                user_id=admin_user_id,
                action="OFFBOARD_EMPLOYEE",
                entity="Employee",
                entity_id=employee_id,
                details=f"Employee ID {employee_id} offboarded. User account deactivated.",
            )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    def get_employee_dashboard_data(self, employee_id: int) -> dict[str, Any]:
        """
        Aggregate all data needed to render an employee's dashboard page.

        Returns a dict with keys:
            - profile:            Employee object with eager-loaded relations.
            - recent_attendance:  Last 5 attendance records.
            - pending_leaves:     All pending leave requests.

        Args:
            employee_id: ID of the employee whose dashboard is being loaded.

        Raises:
            EmployeeNotFoundError: If the employee does not exist.
        """
        employee = self._employee_dao.get_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFoundError(employee_id)

        today = date.today()
        # Last 30 days of attendance as a window for "recent" records
        from datetime import timedelta
        start_of_window = today - timedelta(days=30)

        recent_attendance = self._attendance_dao.get_date_range(
            employee_id=employee_id,
            start_date=start_of_window,
            end_date=today,
        )

        pending_leaves = self._leave_dao.get_by_employee(
            employee_id=employee_id,
            limit=5,
        )

        return {
            "profile": employee,
            "recent_attendance": recent_attendance[-5:],   # last 5 records
            "pending_leaves": pending_leaves,
        }
