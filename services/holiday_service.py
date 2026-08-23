"""
services/holiday_service.py
============================
HR Admin management of the corporate holiday calendar.

Transaction boundary:
  - add_holiday()    → inserts a Holiday record, commits.
  - remove_holiday() → deletes a Holiday record, commits.
"""
from __future__ import annotations

from datetime import date

from config.database import db
from dao.holiday_dao import HolidayDAO
from models.holiday import Holiday
from services.audit_service import AuditService
from services.exceptions import HolidayConflictError, HolidayNotFoundError


class HolidayService:
    """Manages company-wide holiday calendar entries."""

    def __init__(self) -> None:
        self._dao = HolidayDAO()
        self._audit = AuditService()

    # ──────────────────────────────────────────────────────────────────────────
    # Public Methods
    # ──────────────────────────────────────────────────────────────────────────

    def add_holiday(
        self,
        name: str,
        holiday_date: date,
        description: str | None,
        admin_user_id: int,
    ) -> Holiday:
        """
        Add a new public holiday to the company calendar.

        Args:
            name:          Display name for the holiday (e.g. 'Diwali').
            holiday_date:  The date of the holiday.
            description:   Optional extra description.
            admin_user_id: ID of the HR Admin making the change (for audit).

        Returns:
            The newly created Holiday record.

        Raises:
            HolidayConflictError: If a holiday already exists for the given date.
        """
        existing = self._dao.get_by_date(holiday_date)
        if existing is not None:
            raise HolidayConflictError(
                f"A holiday named '{existing.name}' already exists on {holiday_date}."
            )

        try:
            holiday = Holiday(
                name=name,
                date=holiday_date,
                description=description,
            )
            db.session.add(holiday)
            db.session.flush()

            self._audit.log_activity(
                user_id=admin_user_id,
                action="ADD_HOLIDAY",
                entity="Holiday",
                entity_id=holiday.id,
                details=f"Holiday '{name}' added on {holiday_date}.",
            )

            db.session.commit()
            return holiday

        except Exception:
            db.session.rollback()
            raise

    def remove_holiday(self, holiday_id: int, admin_user_id: int) -> None:
        """
        Remove a holiday from the company calendar.

        Args:
            holiday_id:    ID of the Holiday to remove.
            admin_user_id: ID of the HR Admin making the change (for audit).

        Raises:
            HolidayNotFoundError: If no holiday exists with the given ID.
        """
        holiday = self._dao.get_by_id(holiday_id)
        if holiday is None:
            raise HolidayNotFoundError(holiday_id)

        try:
            holiday_name = holiday.name
            db.session.delete(holiday)

            self._audit.log_activity(
                user_id=admin_user_id,
                action="REMOVE_HOLIDAY",
                entity="Holiday",
                entity_id=holiday_id,
                details=f"Holiday '{holiday_name}' (ID={holiday_id}) removed.",
            )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    def update_holiday(
        self,
        holiday_id: int,
        name: str,
        holiday_date: date,
        description: str | None,
        admin_user_id: int,
    ) -> Holiday:
        """
        Update an existing holiday's name, date, and/or description.

        Raises:
            HolidayNotFoundError:  If no holiday with holiday_id exists.
            HolidayConflictError:  If the new date is already taken by another holiday.
        """
        holiday = self._dao.get_by_id(holiday_id)
        if holiday is None:
            raise HolidayNotFoundError(holiday_id)

        # Check date conflict only if date is changing
        if holiday_date != holiday.date:
            conflict = self._dao.get_by_date(holiday_date)
            if conflict is not None:
                raise HolidayConflictError(
                    f"Another holiday '{conflict.name}' already exists on {holiday_date}."
                )

        try:
            old_info = f"{holiday.name} on {holiday.date}"
            holiday.name = name
            holiday.date = holiday_date
            holiday.description = description

            self._audit.log_activity(
                user_id=admin_user_id,
                action="UPDATE_HOLIDAY",
                entity="Holiday",
                entity_id=holiday_id,
                details=f"Holiday updated (was: {old_info}) → '{name}' on {holiday_date}.",
            )

            db.session.commit()
            return holiday

        except Exception:
            db.session.rollback()
            raise
