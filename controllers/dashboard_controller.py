"""
controllers/dashboard_controller.py
===================================
Main dashboard for authenticated users.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import EmployeeService
from models.user import User

dashboard_bp = Blueprint('dashboard', __name__)
employee_service = EmployeeService()

@dashboard_bp.route('/')
@jwt_required()
def index():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))
    employee = user.employee

    # HR/Managers get an overview, normal employees might just see their own stats.
    if employee:
        dashboard_data = employee_service.get_employee_dashboard_data(employee.id)
    else:
        dashboard_data = {}
    
    return render_template('dashboard/index.html', data=dashboard_data, employee=employee)
