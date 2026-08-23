from typing import List, Optional
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import joinedload
from config.database import db
from models.leave_request import LeaveRequest
from models.leave_balance import LeaveBalance
from models.leave_type import LeaveType
from dao.base_dao import BaseDAO

class LeaveTypeDAO(BaseDAO):
    def __init__(self):
        super().__init__(LeaveType)

class LeaveBalanceDAO(BaseDAO):
    def __init__(self):
        super().__init__(LeaveBalance)

    def get_balance(self, employee_id: int, leave_type_id: int, year: int) -> Optional[LeaveBalance]:
        """Fetch the leave balance for a specific employee, leave type, and year."""
        return db.session.query(LeaveBalance)\
            .filter(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.year == year
            ).first()

    def get_all_by_employee(self, employee_id: int) -> List[LeaveBalance]:
        return db.session.query(LeaveBalance)\
            .options(joinedload(LeaveBalance.leave_type))\
            .filter(LeaveBalance.employee_id == employee_id).all()

    def deduct_balance(self, balance_id: int, days_to_deduct: float) -> Optional[LeaveBalance]:
        """Deduct used days from the balance dynamically."""
        balance = self.get_by_id(balance_id)
        if balance:
            balance.used_days += days_to_deduct
        return balance

class LeaveRequestDAO(BaseDAO):
    def __init__(self):
        super().__init__(LeaveRequest)

    def get_by_employee(self, employee_id: int, offset: int = 0, limit: int = 20) -> List[LeaveRequest]:
        """Fetch all leave requests for a specific employee."""
        return db.session.query(LeaveRequest)\
            .options(joinedload(LeaveRequest.leave_type))\
            .filter(LeaveRequest.employee_id == employee_id)\
            .order_by(LeaveRequest.created_at.desc())\
            .offset(offset).limit(limit).all()

    def get_pending_for_manager(self, manager_id: int, offset: int = 0, limit: int = 20) -> List[LeaveRequest]:
        """Fetch all pending leave requests submitted by a manager's direct reports."""
        from models.employee import Employee
        return db.session.query(LeaveRequest)\
            .join(Employee, LeaveRequest.employee_id == Employee.id)\
            .options(joinedload(LeaveRequest.employee), joinedload(LeaveRequest.leave_type))\
            .filter(Employee.manager_id == manager_id, LeaveRequest.status == 'Pending')\
            .order_by(LeaveRequest.created_at.asc())\
            .offset(offset).limit(limit).all()

    def get_all_pending(self, offset: int = 0, limit: int = 20) -> List[LeaveRequest]:
        return db.session.query(LeaveRequest)\
            .options(joinedload(LeaveRequest.employee), joinedload(LeaveRequest.leave_type))\
            .filter(LeaveRequest.status == 'Pending')\
            .order_by(LeaveRequest.created_at.asc())\
            .offset(offset).limit(limit).all()

    def update_status(self, request_id: int, status: str, comment: Optional[str] = None) -> Optional[LeaveRequest]:
        """Approve or reject a leave request with an optional manager comment."""
        request = self.get_by_id(request_id)
        if request:
            request.status = status
            if comment:
                request.manager_comment = comment
        return request
