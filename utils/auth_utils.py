"""
utils/auth_utils.py
===================
Utilities for authentication and authorization.
Includes role-based access control (RBAC) decorators and context processors.
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from models.user import User

def role_required(*roles):
    """
    Custom decorator to protect endpoints based on user roles.
    Assumes `verify_jwt_in_request()` has been called or is handled by `@jwt_required()`.
    However, to allow stacking without `@jwt_required()`, we verify it here too.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', 'Employee')
            
            if user_role not in roles:
                flash(f"Access denied: Requires one of {roles} roles.", "danger")
                # Usually redirect to the dashboard
                return redirect(url_for('dashboard.index'))
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def inject_current_user():
    """
    Context processor to inject the current user and employee into Jinja2 templates.
    This runs before rendering any template.
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(user_id)
            if user:
                return dict(
                    current_user=user,
                    current_employee=user.employee
                )
    except Exception:
        # Ignore decoding errors here; unauthorized_loader will handle hard errors on protected routes
        pass
    
    return dict(current_user=None, current_employee=None)
