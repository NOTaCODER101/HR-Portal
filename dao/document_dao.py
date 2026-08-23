from typing import List
from config.database import db
from models.employee_document import EmployeeDocument
from dao.base_dao import BaseDAO

class DocumentDAO(BaseDAO):
    def __init__(self):
        super().__init__(EmployeeDocument)

    def get_by_employee(self, employee_id: int) -> List[EmployeeDocument]:
        """Retrieve all document metadata associated with an employee."""
        return db.session.query(EmployeeDocument)\
            .filter(EmployeeDocument.employee_id == employee_id)\
            .order_by(EmployeeDocument.uploaded_at.desc()).all()
