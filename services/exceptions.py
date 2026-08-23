"""
services/exceptions.py
======================
All custom domain exceptions for the HR Portal Service Layer.

Raising named exceptions instead of returning raw booleans or strings
gives controllers a clean contract: catch a specific exception, return
the appropriate HTTP response or flash message.
"""


class HRPortalBaseError(Exception):
    """Base class for all HR Portal domain exceptions."""
    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)


# ── Authentication ────────────────────────────────────────────────────────────

class InvalidCredentialsError(HRPortalBaseError):
    """Raised when username/password combination does not match any active user."""
    def __init__(self, message: str = "Invalid username or password."):
        super().__init__(message)


class AccountInactiveError(HRPortalBaseError):
    """Raised when a deactivated user attempts to log in."""
    def __init__(self, message: str = "Your account has been deactivated. Please contact HR."):
        super().__init__(message)


class UnauthorizedActionError(HRPortalBaseError):
    """Raised when a user attempts an action they are not authorized to perform."""
    def __init__(self, message: str = "You are not authorized to perform this action."):
        super().__init__(message)


# ── Attendance ────────────────────────────────────────────────────────────────

class DuplicateCheckInError(HRPortalBaseError):
    """Raised when an employee tries to check in more than once on the same day."""
    def __init__(self, message: str = "You have already checked in for today."):
        super().__init__(message)


class NoActiveCheckInError(HRPortalBaseError):
    """Raised when an employee tries to check out without a prior check-in."""
    def __init__(self, message: str = "No active check-in found for today. Please check in first."):
        super().__init__(message)


# ── Leave Management ──────────────────────────────────────────────────────────

class InsufficientLeaveBalanceError(HRPortalBaseError):
    """Raised when an employee requests more leave days than their available balance."""
    def __init__(self, available: float, requested: float):
        message = (
            f"Insufficient leave balance. "
            f"You have {available:.1f} days available but requested {requested:.1f} days."
        )
        self.available = available
        self.requested = requested
        super().__init__(message)


class LeaveRequestNotFoundError(HRPortalBaseError):
    """Raised when a leave request ID does not exist."""
    def __init__(self, request_id: int):
        super().__init__(f"Leave request #{request_id} was not found.")


# ── Holiday ───────────────────────────────────────────────────────────────────

class HolidayConflictError(HRPortalBaseError):
    """Raised when an HR Admin tries to add a holiday on an already-registered date."""
    def __init__(self, message: str = "A holiday already exists for this date."):
        super().__init__(message)


class HolidayNotFoundError(HRPortalBaseError):
    """Raised when a holiday ID does not exist."""
    def __init__(self, holiday_id: int):
        super().__init__(f"Holiday #{holiday_id} was not found.")


# ── Employee ──────────────────────────────────────────────────────────────────

class EmployeeNotFoundError(HRPortalBaseError):
    """Raised when an employee record cannot be located."""
    def __init__(self, identifier: str | int):
        super().__init__(f"Employee '{identifier}' was not found.")


class DuplicateUsernameError(HRPortalBaseError):
    """Raised when onboarding an employee with a username that already exists."""
    def __init__(self, username: str):
        super().__init__(f"Username '{username}' is already taken. Please choose another.")


# ── Documents ─────────────────────────────────────────────────────────────────

class FileUploadError(HRPortalBaseError):
    """Raised when a file upload fails validation or disk write."""
    def __init__(self, message: str = "File upload failed. Please check the file type and size."):
        super().__init__(message)
