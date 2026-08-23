"""
services/__init__.py
====================
Convenience re-exports for the services package.
Import services directly from this module in controllers:

    from services import AuthService, LeaveService
"""
from .auth_service import AuthService
from .employee_service import EmployeeService
from .attendance_service import AttendanceService
from .leave_service import LeaveService
from .holiday_service import HolidayService
from .document_service import DocumentService
from .audit_service import AuditService
from .exceptions import (
    HRPortalBaseError,
    InvalidCredentialsError,
    AccountInactiveError,
    UnauthorizedActionError,
    DuplicateCheckInError,
    NoActiveCheckInError,
    InsufficientLeaveBalanceError,
    LeaveRequestNotFoundError,
    HolidayConflictError,
    HolidayNotFoundError,
    EmployeeNotFoundError,
    DuplicateUsernameError,
    FileUploadError,
)

__all__ = [
    # Services
    "AuthService",
    "EmployeeService",
    "AttendanceService",
    "LeaveService",
    "HolidayService",
    "DocumentService",
    "AuditService",
    # Exceptions
    "HRPortalBaseError",
    "InvalidCredentialsError",
    "AccountInactiveError",
    "UnauthorizedActionError",
    "DuplicateCheckInError",
    "NoActiveCheckInError",
    "InsufficientLeaveBalanceError",
    "LeaveRequestNotFoundError",
    "HolidayConflictError",
    "HolidayNotFoundError",
    "EmployeeNotFoundError",
    "DuplicateUsernameError",
    "FileUploadError",
]
