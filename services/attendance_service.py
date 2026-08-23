"""
services/attendance_service.py
==============================
Daily check-in / check-out logic with duplicate prevention.

Transaction boundary:
  - process_check_in()  → inserts a new Attendance record, commits.
  - process_check_out() → updates the existing record's check_out, commits.
"""
from __future__ import annotations

from datetime import date, datetime

from config.database import db
from dao.attendance_dao import AttendanceDAO
from models.attendance import Attendance
from services.exceptions import DuplicateCheckInError, NoActiveCheckInError


class AttendanceService:
    """Handles employee check-in and check-out workflows."""

    def __init__(self) -> None:
        self._dao = AttendanceDAO()

    # ──────────────────────────────────────────────────────────────────────────
    # Public Methods
    # ──────────────────────────────────────────────────────────────────────────

    def process_check_in(self, employee_id: int) -> Attendance:
        """
        Record a check-in for the current date.

        Prevents duplicate check-ins by querying for an existing record
        for today before creating a new one.

        Args:
            employee_id: ID of the employee checking in.

        Returns:
            The newly created Attendance record.

        Raises:
            DuplicateCheckInError: If the employee has already checked in today.
        """
        today = date.today()
        existing = self._dao.get_by_date(employee_id, today)

        if existing is not None:
            raise DuplicateCheckInError()

        try:
            record = Attendance(
                employee_id=employee_id,
                date=today,
                check_in=datetime.now().time(),
            )
            db.session.add(record)
            db.session.commit()
            return record

        except Exception:
            db.session.rollback()
            raise

    def process_check_out(self, employee_id: int) -> Attendance:
        """
        Record a check-out for the current date.

        Validates that the employee has already checked in today before
        writing the check_out timestamp.

        Args:
            employee_id: ID of the employee checking out.

        Returns:
            The updated Attendance record.

        Raises:
            NoActiveCheckInError: If there is no check-in record for today.
        """
        today = date.today()
        record = self._dao.get_by_date(employee_id, today)

        if record is None or record.check_in is None:
            raise NoActiveCheckInError()

        try:
            record.check_out = datetime.now().time()
            db.session.commit()
            return record

        except Exception:
            db.session.rollback()
            raise
