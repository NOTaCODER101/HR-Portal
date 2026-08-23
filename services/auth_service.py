"""
services/auth_service.py
========================
Authentication workflows using Flask-JWT-Extended.

Responsibilities:
  - Validate credentials and issue JWT access + refresh tokens stored in
    secure HttpOnly cookies.
  - Revoke tokens server-side via the JWTBlocklist table on logout.
  - Provide a refresh flow to silently renew an expiring access token.
  - Change password with old-password verification.

Transaction boundary: commit() is called here for login (last_login update)
and logout (blocklist insert). All other callers should wrap in their own
transaction if needed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

# pyrefly: ignore [missing-import]
from flask import Response
# pyrefly: ignore [missing-import]
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from werkzeug.security import check_password_hash, generate_password_hash

from config.database import db
from dao.user_dao import UserDAO
from models.jwt_blocklist import JWTBlocklist
from services.audit_service import AuditService
from services.exceptions import (
    AccountInactiveError,
    InvalidCredentialsError,
)

if TYPE_CHECKING:
    from models.user import User


class AuthService:
    """Handles all authentication and token lifecycle operations."""

    def __init__(self) -> None:
        self._user_dao = UserDAO()
        self._audit = AuditService()

    # ──────────────────────────────────────────────────────────────────────────
    # Public Methods
    # ──────────────────────────────────────────────────────────────────────────

    def login_user(self, username: str, password: str, response: Response) -> "User":
        """
        Validate credentials and set JWT cookies on the response.

        Args:
            username: The submitted username.
            password: The submitted plaintext password.
            response: The Flask Response object to attach JWT cookies to.

        Returns:
            The authenticated User object.

        Raises:
            InvalidCredentialsError: If the username does not exist or the
                                     password does not match.
            AccountInactiveError:    If the account has been deactivated.
        """
        user = self._user_dao.get_by_username(username)

        if user is None or not check_password_hash(user.password_hash, password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountInactiveError()

        # Build custom JWT claims so controllers can read role without a DB hit
        additional_claims = {
            "role": user.role,
            "employee_id": user.employee.id if user.employee else None,
        }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims=additional_claims,
        )

        # Attach tokens as secure HttpOnly cookies
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        # Record last login timestamp
        user.last_login = datetime.now(timezone.utc)

        try:
            self._audit.log_activity(
                user_id=user.id,
                action="LOGIN",
                entity="User",
                entity_id=user.id,
                details=f"User '{username}' logged in successfully.",
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return user

    def logout_user(self, response: Response) -> None:
        """
        Revoke the current JWT by adding its jti to the blocklist.

        Args:
            response: The Flask Response object to clear JWT cookies from.
        """
        jwt_payload = get_jwt()
        jti = jwt_payload.get("jti")
        user_id = get_jwt_identity()

        try:
            blocklist_entry = JWTBlocklist(jti=jti)
            db.session.add(blocklist_entry)
            self._audit.log_activity(
                user_id=int(user_id) if user_id else None,
                action="LOGOUT",
                entity="User",
                entity_id=int(user_id) if user_id else None,
                details=f"JWT jti={jti} revoked.",
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        finally:
            # Always clear the cookies even if the DB write fails
            unset_jwt_cookies(response)

    def refresh_token(self, response: Response) -> None:
        """
        Issue a new access token using a valid refresh token cookie.
        Called from a @jwt_required(refresh=True) protected endpoint.

        Args:
            response: The Flask Response object to attach the new access cookie to.
        """
        identity = get_jwt_identity()
        jwt_payload = get_jwt()

        additional_claims = {
            "role": jwt_payload.get("role"),
            "employee_id": jwt_payload.get("employee_id"),
        }

        new_access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims,
        )
        set_access_cookies(response, new_access_token)

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> None:
        """
        Update a user's password after verifying the old one.

        Args:
            user_id:      The ID of the user changing their password.
            old_password: The current plaintext password for verification.
            new_password: The new plaintext password to hash and store.

        Raises:
            InvalidCredentialsError: If old_password does not match the stored hash.
        """
        user = self._user_dao.get_by_id(user_id)

        if user is None or not check_password_hash(user.password_hash, old_password):
            raise InvalidCredentialsError("Current password is incorrect.")

        try:
            self._user_dao.update_password(user_id, generate_password_hash(new_password))
            self._audit.log_activity(
                user_id=user_id,
                action="CHANGE_PASSWORD",
                entity="User",
                entity_id=user_id,
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
