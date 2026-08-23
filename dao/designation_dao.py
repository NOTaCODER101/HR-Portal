from config.database import db
from models.designation import Designation
from dao.base_dao import BaseDAO
from sqlalchemy import func

class DesignationDAO(BaseDAO):
    def __init__(self):
        super().__init__(Designation)

    def has_employees(self, designation_id: int) -> bool:
        """Structural check: Verify if a designation is currently assigned to employees."""
        from models.employee import Employee
        count = db.session.query(func.count(Employee.id))\
            .filter(Employee.designation_id == designation_id).scalar()
        return count > 0

    def delete(self, record_id: int) -> bool:
        """Override delete to enforce structural checks."""
        if self.has_employees(record_id):
            raise ValueError("Cannot delete designation because it is assigned to active employees.")
        return super().delete(record_id)
