from typing import List, Optional, Dict, Any
from sqlalchemy.orm import joinedload
from config.database import db
from models.employee import Employee
from dao.base_dao import BaseDAO

class EmployeeDAO(BaseDAO):
    def __init__(self):
        super().__init__(Employee)

    def get_by_id(self, record_id: int) -> Optional[Employee]:
        """Override to use eager loading for relations to prevent N+1 queries."""
        return db.session.query(Employee)\
            .options(
                joinedload(Employee.department),
                joinedload(Employee.designation),
                joinedload(Employee.user)
            )\
            .filter(Employee.id == record_id).first()

    def get_by_user_id(self, user_id: int) -> Optional[Employee]:
        """Fetch an employee profile connected to a specific user ID."""
        return db.session.query(Employee)\
            .options(joinedload(Employee.department), joinedload(Employee.designation))\
            .filter(Employee.user_id == user_id).first()

    def search_employees(self, filters: Dict[str, Any], offset: int = 0, limit: int = 50) -> List[Employee]:
        """Search and filter employees by various parameters."""
        query = db.session.query(Employee).options(
            joinedload(Employee.department),
            joinedload(Employee.designation)
        )

        if 'first_name' in filters:
            query = query.filter(Employee.first_name.ilike(f"%{filters['first_name']}%"))
        if 'last_name' in filters:
            query = query.filter(Employee.last_name.ilike(f"%{filters['last_name']}%"))
        if 'email' in filters:
            query = query.filter(Employee.email.ilike(f"%{filters['email']}%"))
        if 'department_id' in filters:
            query = query.filter(Employee.department_id == filters['department_id'])
        if 'manager_id' in filters:
            query = query.filter(Employee.manager_id == filters['manager_id'])

        return query.offset(offset).limit(limit).all()

    def get_team_members(self, manager_id: int) -> List[Employee]:
        """Fetch all employees reporting to a specific manager."""
        return db.session.query(Employee)\
            .options(joinedload(Employee.department), joinedload(Employee.designation))\
            .filter(Employee.manager_id == manager_id).all()
