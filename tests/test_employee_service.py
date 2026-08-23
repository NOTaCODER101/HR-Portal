"""
tests/test_employee_service.py
================================
Unit tests for EmployeeService — onboarding and offboarding flows.
"""
import pytest
from datetime import date

from services.employee_service import EmployeeService
from services.exceptions import DuplicateUsernameError, EmployeeNotFoundError


class TestEmployeeServiceOnboard:
    """Tests for EmployeeService.onboard_employee()"""

    def _make_data(self, username='emp_test'):
        return {
            'username': username,
            'role': 'Employee',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': f'{username}@example.com',
            'date_of_joining': date.today(),
        }

    def test_onboard_creates_user_and_employee(self, app, db, admin_user):
        """Onboarding should create both a User record and an Employee record."""
        from models.user import User
        from models.employee import Employee

        with app.app_context():
            service = EmployeeService()
            new_emp = service.onboard_employee(
                data=self._make_data('new_hire_01'),
                admin_user_id=admin_user.id,
            )

            assert new_emp.id is not None
            assert new_emp.first_name == 'Jane'

            created_user = User.query.filter_by(username='new_hire_01').first()
            assert created_user is not None
            assert created_user.role == 'Employee'

    def test_onboard_duplicate_username_raises(self, app, db, admin_user):
        """Onboarding a username that already exists must raise DuplicateUsernameError."""
        with app.app_context():
            service = EmployeeService()
            service.onboard_employee(
                data=self._make_data('dup_user'),
                admin_user_id=admin_user.id,
            )
            # Second attempt with same username
            with pytest.raises(DuplicateUsernameError):
                service.onboard_employee(
                    data=self._make_data('dup_user'),
                    admin_user_id=admin_user.id,
                )


class TestEmployeeServiceOffboard:
    """Tests for EmployeeService.offboard_employee()"""

    def test_offboard_deactivates_user(self, app, db, admin_user):
        """Offboarding should set User.is_active to False."""
        from models.user import User

        with app.app_context():
            service = EmployeeService()
            new_emp = service.onboard_employee(
                data={
                    'username': 'leaving_emp',
                    'role': 'Employee',
                    'first_name': 'John',
                    'last_name': 'Leaving',
                    'email': 'leaving@example.com',
                    'date_of_joining': date.today(),
                },
                admin_user_id=admin_user.id,
            )

            service.offboard_employee(new_emp.id, admin_user.id)

            user = User.query.filter_by(username='leaving_emp').first()
            assert user is not None
            assert user.is_active is False

    def test_offboard_nonexistent_raises(self, app, db, admin_user):
        """Offboarding a non-existent employee ID must raise EmployeeNotFoundError."""
        with app.app_context():
            service = EmployeeService()
            with pytest.raises(EmployeeNotFoundError):
                service.offboard_employee(employee_id=999999, admin_user_id=admin_user.id)
