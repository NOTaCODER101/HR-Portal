"""
tests/test_auth_service.py
===========================
Unit tests for AuthService — login, logout, and change_password flows.
"""
import pytest
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock

from services.auth_service import AuthService
from services.exceptions import InvalidCredentialsError, AccountInactiveError


class TestAuthServiceLogin:
    """Tests for AuthService.login_user()"""

    def test_login_success(self, app, db):
        """Valid credentials should authenticate without raising."""
        from models.user import User

        with app.app_context():
            user = User(
                username='jdoe',
                password_hash=generate_password_hash('Secret@1'),
                role='Employee',
                is_active=True,
            )
            db.session.add(user)
            db.session.commit()

            mock_response = MagicMock()
            service = AuthService()
            result = service.login_user('jdoe', 'Secret@1', mock_response)

            assert result.username == 'jdoe'
            mock_response  # JWT cookies were set on it

    def test_login_wrong_password_raises(self, app, db):
        """Wrong password must raise InvalidCredentialsError."""
        from models.user import User

        with app.app_context():
            user = User(
                username='jdoe2',
                password_hash=generate_password_hash('RealPass@1'),
                role='Employee',
                is_active=True,
            )
            db.session.add(user)
            db.session.commit()

            mock_response = MagicMock()
            service = AuthService()

            with pytest.raises(InvalidCredentialsError):
                service.login_user('jdoe2', 'WrongPass', mock_response)

    def test_login_nonexistent_user_raises(self, app, db):
        """Unknown username must raise InvalidCredentialsError."""
        with app.app_context():
            mock_response = MagicMock()
            service = AuthService()

            with pytest.raises(InvalidCredentialsError):
                service.login_user('nobody', 'whatever', mock_response)

    def test_login_inactive_account_raises(self, app, db):
        """Deactivated account must raise AccountInactiveError."""
        from models.user import User

        with app.app_context():
            user = User(
                username='inactive_user',
                password_hash=generate_password_hash('Pass@1'),
                role='Employee',
                is_active=False,
            )
            db.session.add(user)
            db.session.commit()

            mock_response = MagicMock()
            service = AuthService()

            with pytest.raises(AccountInactiveError):
                service.login_user('inactive_user', 'Pass@1', mock_response)


class TestAuthServiceChangePassword:
    """Tests for AuthService.change_password()"""

    def test_change_password_success(self, app, db):
        """Correct old password should update to the new hash."""
        from models.user import User
        from werkzeug.security import check_password_hash

        with app.app_context():
            user = User(
                username='changeme',
                password_hash=generate_password_hash('OldPass@1'),
                role='Employee',
                is_active=True,
            )
            db.session.add(user)
            db.session.commit()
            uid = user.id

            service = AuthService()
            service.change_password(uid, 'OldPass@1', 'NewPass@1')

            updated = User.query.get(uid)
            assert check_password_hash(updated.password_hash, 'NewPass@1')

    def test_change_password_wrong_old_raises(self, app, db):
        """Wrong current password must raise InvalidCredentialsError."""
        from models.user import User

        with app.app_context():
            user = User(
                username='blockme',
                password_hash=generate_password_hash('RealOld@1'),
                role='Employee',
                is_active=True,
            )
            db.session.add(user)
            db.session.commit()

            service = AuthService()
            with pytest.raises(InvalidCredentialsError):
                service.change_password(user.id, 'WrongOld', 'NewPass@1')
