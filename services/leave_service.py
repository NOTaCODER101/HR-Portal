"""
services/leave_service.py
=========================
Complex leave balance calculation, holiday-aware business day counting,
and manager-gated approval workflows.

Transaction boundary:
  - apply_for_leave()        → creates LeaveRequest, commits.
  - process_leave_approval() → updates status + optionally deducts balance, commits.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from config.database import db
from dao.employee_dao import EmployeeDAO
from dao.holiday_dao import HolidayDAO
from dao.leave_dao import LeaveBalanceDAO, LeaveRequestDAO
from models.leave_request import LeaveRequest
from services.audit_service import AuditService
from services.exceptions import (
    EmployeeNotFoundError,
    InsufficientLeaveBalanceError,
    LeaveRequestNotFoundError,
    UnauthorizedActionError,
)


class LeaveService:
    """Handles leave application, balance checks, and manager approval flows."""

    def __init__(self) -> None:
        self._leave_request_dao = LeaveRequestDAO()
        self._leave_balance_dao = LeaveBalanceDAO()
        self._holiday_dao = HolidayDAO()
        self._employee_dao = EmployeeDAO()
        self._audit = AuditService()

    # ──────────────────────────────────────────────────────────────────────────
    # Private Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _calculate_business_days(self, start_date: date, end_date: date) -> float:
        """
        Count valid business days between two dates, excluding weekends and
        any company holidays recorded in the Holiday table.

        Args:
            start_date: Inclusive start of the leave period.
            end_date:   Inclusive end of the leave period.

        Returns:
            The number of valid business days as a float.
        """
        # Pre-fetch all holidays in the year range as a set of dates for O(1) lookups
        holiday_dates: set[date] = set()
        for year in range(start_date.year, end_date.year + 1):
            for h in self._holiday_dao.get_holidays_by_year(year):
                holiday_dates.add(h.date)

        business_days = 0.0
        current = start_date
        while current <= end_date:
            # weekday() returns 0=Mon … 4=Fri, 5=Sat, 6=Sun
            if current.weekday() < 5 and current not in holiday_dates:
                business_days += 1.0
            current += timedelta(days=1)

        return business_days

    # ──────────────────────────────────────────────────────────────────────────
    # Public Methods
    # ──────────────────────────────────────────────────────────────────────────

    def apply_for_leave(
        self,
        employee_id: int,
        leave_type_id: int,
        start_date: date,
        end_date: date,
        reason: str,
    ) -> LeaveRequest:
        """
        Submit a leave application on behalf of an employee.

        Steps:
          1. Calculate valid business days (excludes weekends + public holidays).
          2. Fetch the employee's leave balance for this year and leave type.
          3. Raise InsufficientLeaveBalanceError if balance is too low.
          4. Create the LeaveRequest in 'Pending' status.
          5. Commit.

        Args:
            employee_id:   The employee applying for leave.
            leave_type_id: The type of leave being requested.
            start_date:    First day of leave (inclusive).
            end_date:      Last day of leave (inclusive).
            reason:        Reason for the leave application.

        Returns:
            The newly created LeaveRequest.

        Raises:
            InsufficientLeaveBalanceError: If the employee's available balance
                                           is less than the calculated days.
        """
        requested_days = self._calculate_business_days(start_date, end_date)
        current_year = start_date.year

        balance = self._leave_balance_dao.get_balance(employee_id, leave_type_id, current_year)

        available_days = 0.0
        if balance is not None:
            available_days = float(balance.allocated_days) - balance.used_days

        if requested_days > available_days:
            raise InsufficientLeaveBalanceError(
                available=available_days,
                requested=requested_days,
            )

        try:
            leave_request = LeaveRequest(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='Pending',
            )
            db.session.add(leave_request)
            db.session.flush()  # Get the new ID

            self._audit.log_activity(
                user_id=employee_id,  # Note: employee_id used as user proxy here
                action="APPLY_LEAVE",
                entity="LeaveRequest",
                entity_id=leave_request.id,
                details=f"Applied for {requested_days:.1f} day(s) of leave type {leave_type_id}.",
            )

            db.session.commit()
            return leave_request

        except Exception:
            db.session.rollback()
            raise

    def process_leave_approval(
        self,
        request_id: int,
        manager_employee_id: int,
        status: str,
        comment: str | None = None,
    ) -> LeaveRequest:
        """
        Approve or reject a leave request, with authorization verification.

        Steps:
          1. Fetch the leave request.
          2. Fetch the requesting employee.
          3. VERIFY that manager_employee_id == employee.manager_id.
             Raises UnauthorizedActionError if not matching.
          4. Update the leave request status and comment.
          5. If status == 'Approved', deduct days from LeaveBalance.
          6. Commit.

        Args:
            request_id:          ID of the LeaveRequest to process.
            manager_employee_id: Employee ID of the manager acting on the request.
            status:              'Approved' or 'Rejected'.
            comment:             Optional manager comment / rejection reason.

        Returns:
            The updated LeaveRequest.

        Raises:
            LeaveRequestNotFoundError: If the request ID does not exist.
            EmployeeNotFoundError:     If the requesting employee does not exist.
            UnauthorizedActionError:   If the manager does not own this employee.
        """
        leave_request = self._leave_request_dao.get_by_id(request_id)
        if leave_request is None:
            raise LeaveRequestNotFoundError(request_id)

        employee = self._employee_dao.get_by_id(leave_request.employee_id)
        if employee is None:
            raise EmployeeNotFoundError(leave_request.employee_id)

        # ── Authorization gate ────────────────────────────────────────────────
        if employee.manager_id != manager_employee_id:
            raise UnauthorizedActionError(
                "You are not the assigned manager for this employee."
            )

        try:
            # Update status and comment
            self._leave_request_dao.update_status(request_id, status, comment)

            # Deduct balance only on approval
            if status == 'Approved':
                days_approved = self._calculate_business_days(
                    leave_request.start_date, leave_request.end_date
                )
                balance = self._leave_balance_dao.get_balance(
                    employee_id=leave_request.employee_id,
                    leave_type_id=leave_request.leave_type_id,
                    year=leave_request.start_date.year,
                )
                if balance is not None:
                    self._leave_balance_dao.deduct_balance(balance.id, days_approved)

            self._audit.log_activity(
                user_id=manager_employee_id,
                action=f"LEAVE_{status.upper()}",
                entity="LeaveRequest",
                entity_id=request_id,
                details=f"Leave request #{request_id} {status.lower()} by manager {manager_employee_id}. Comment: {comment}",
            )

            db.session.commit()
            return leave_request

        except Exception:
            db.session.rollback()
            raise
