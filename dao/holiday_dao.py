from typing import List, Optional
from datetime import date
# pyrefly: ignore [missing-import]
from sqlalchemy import extract
from config.database import db
from models.holiday import Holiday
from dao.base_dao import BaseDAO

class HolidayDAO(BaseDAO):
    def __init__(self):
        super().__init__(Holiday)

    def get_by_date(self, target_date: date) -> Optional[Holiday]:
        """Check if a specific date is a company holiday (used for leave calculations)."""
        return db.session.query(Holiday).filter(Holiday.date == target_date).first()

    def get_all_ordered(self) -> List[Holiday]:
        """Fetch all holidays sorted by date ascending."""
        return db.session.query(Holiday).order_by(Holiday.date.asc()).all()

    def get_holidays_by_year(self, year: int) -> List[Holiday]:
        """Fetch all holidays for a specific year to display on the calendar."""
        return db.session.query(Holiday)\
            .filter(extract('year', Holiday.date) == year)\
            .order_by(Holiday.date.asc()).all()
