"""
controllers/leave_controller.py
===============================
Apply for leaves, view balances, and manager approvals.
"""
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import LeaveService
from services.exceptions import HRPortalBaseError
from models.user import User
from dao.leave_dao import LeaveRequestDAO, LeaveTypeDAO, LeaveBalanceDAO
from utils.auth_utils import role_required

leave_bp = Blueprint('leave', __name__)
leave_service = LeaveService()
leave_request_dao = LeaveRequestDAO()
leave_type_dao = LeaveTypeDAO()
leave_balance_dao = LeaveBalanceDAO()

@leave_bp.route('/apply', methods=['GET', 'POST'])
@jwt_required()
def apply():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.employee:
        flash("You are not registered as an employee.", "danger")
        return redirect(url_for('dashboard.index'))

    if request.method == 'GET':
        leave_types = leave_type_dao.get_all()
        return render_template('leave/apply.html', leave_types=leave_types)

    leave_type_id = int(request.form.get('leave_type_id') or 0)
    start_date = datetime.strptime(request.form.get('start_date') or "", '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form.get('end_date') or "", '%Y-%m-%d').date()
    reason = request.form.get('reason') or ""

    try:
        leave_service.apply_for_leave(user.employee.id, leave_type_id, start_date, end_date, reason)
        flash("Leave request submitted successfully.", "success")
        return redirect(url_for('leave.my_leaves'))
    except HRPortalBaseError as e:
        flash(str(e), "danger")
        return redirect(url_for('leave.apply'))
    except Exception as e:
        flash("An error occurred while submitting leave request.", "danger")
        return redirect(url_for('leave.apply'))

@leave_bp.route('/my-leaves', methods=['GET'])
@jwt_required()
def my_leaves():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.employee:
        flash("You are not registered as an employee.", "danger")
        return redirect(url_for('dashboard.index'))

    balances = leave_balance_dao.get_all_by_employee(user.employee.id)
    requests = leave_request_dao.get_by_employee(user.employee.id)
    return render_template('leave/my_leaves.html', balances=balances, requests=requests)

@leave_bp.route('/requests', methods=['GET', 'POST'])
@jwt_required()
@role_required('Manager', 'HR Admin')
def manage_requests():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        if user.role == 'HR Admin':
            pending_requests = leave_request_dao.get_all_pending()
        else:
            if not user.employee:
                flash("You are not registered as an employee.", "danger")
                return redirect(url_for('dashboard.index'))
            pending_requests = leave_request_dao.get_pending_for_manager(user.employee.id)

        return render_template('leave/requests.html', requests=pending_requests)

    # POST: approve/reject
    request_id = int(request.form.get('request_id') or 0)
    action = request.form.get('action') or ""
    comment = request.form.get('comment', '')

    try:
        # HR Admin bypasses manager check; use employee.id if available else 0
        manager_emp_id = user.employee.id if user.employee else 0
        leave_service.process_leave_approval(request_id, manager_emp_id, action, comment)
        flash(f"Leave request {action.lower() if action else ''} successfully.", "success")
    except HRPortalBaseError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash("An error occurred while processing the leave request.", "danger")

    return redirect(url_for('leave.manage_requests'))

