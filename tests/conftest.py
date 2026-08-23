"""
tests/conftest.py
=================
Shared pytest fixtures for the HR Portal test suite.
Uses an in-memory SQLite database so no MySQL is required for tests.
"""
import pytest
from app import create_app
from config.database import db as _db
import models  # noqa: F401 — ensures all models are registered


@pytest.fixture(scope='session')
def app():
    """Create a Flask app configured for testing with SQLite in-memory DB."""
    test_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_COOKIE_CSRF_PROTECT': False,   # Disable CSRF for tests
        'WTF_CSRF_ENABLED': False,
    })
    return test_app


@pytest.fixture(scope='function')
def db(app):
    """Create all tables before each test, drop after."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Flask test client with an active app context."""
    return app.test_client()


@pytest.fixture(scope='function')
def admin_user(db, app):
    """Create and return a seeded HR Admin user for use in tests."""
    from models.user import User
    from models.employee import Employee
    from werkzeug.security import generate_password_hash
    from datetime import date

    with app.app_context():
        user = User(
            username='testadmin',
            password_hash=generate_password_hash('Test@1234'),
            role='HR Admin',
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()

        emp = Employee(
            user_id=user.id,
            first_name='Test',
            last_name='Admin',
            email='testadmin@hrportal.com',
            date_of_joining=date.today(),
        )
        db.session.add(emp)
        db.session.commit()
        
        # Return a simple object or dict, or just keep it in session, 
        # or we can yield it inside the context.
        # But easier is just to re-fetch or use db.session.refresh(user) if we had a session.
        # Let's just return the user object but we must ensure we only access its ID in tests,
        # or we just yield it inside the app context.
        yield user
