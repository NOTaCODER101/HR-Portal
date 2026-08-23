from config.database import db
from models.department import Department
from dao.base_dao import BaseDAO
from sqlalchemy import func

class DepartmentDAO(BaseDAO):
    def __init__(self):
        super().__init__(Department)

    def has_employees(self, department_id: int) -> bool:
        """Structural check: Verify if a department currently has assigned employees."""
        from models.employee import Employee
        count = db.session.query(func.count(Employee.id))\
            .filter(Employee.department_id == department_id).scalar()
        return count > 0

    def delete(self, record_id: int) -> bool:
        """Override delete to enforce structural checks."""
        if self.has_employees(record_id):
            raise ValueError("Cannot delete department because it has active employees assigned.")
        return super().delete(record_id)
