from typing import List, Optional
from datetime import date
from config.database import db
from models.attendance import Attendance
from dao.base_dao import BaseDAO

class AttendanceDAO(BaseDAO):
    def __init__(self):
        super().__init__(Attendance)

    def get_by_date(self, employee_id: int, target_date: date) -> Optional[Attendance]:
        """Fetch attendance record for a specific employee on a specific date (duplicate check)."""
        return db.session.query(Attendance)\
            .filter(Attendance.employee_id == employee_id, Attendance.date == target_date).first()

    def get_by_employee_id(self, employee_id: int, offset: int = 0, limit: int = 50) -> List[Attendance]:
        """Fetch attendance records for a specific employee."""
        return db.session.query(Attendance)\
            .filter(Attendance.employee_id == employee_id)\
            .order_by(Attendance.date.desc())\
            .offset(offset).limit(limit).all()

    def get_date_range(self, employee_id: int, start_date: date, end_date: date) -> List[Attendance]:
        """Fetch attendance records within a specific date range for reporting/analytics."""
        return db.session.query(Attendance)\
            .filter(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).order_by(Attendance.date.asc()).all()

    def get_all_by_date(self, target_date: date, offset: int = 0, limit: int = 50) -> List[Attendance]:
        """Fetch all attendance records for a given date across the company."""
        return db.session.query(Attendance)\
            .filter(Attendance.date == target_date)\
            .offset(offset).limit(limit).all()
