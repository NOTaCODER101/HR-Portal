"""
controllers/attendance_controller.py
====================================
Check in, check out, and viewing attendance logs.
"""
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import AttendanceService
from services.exceptions import HRPortalBaseError
from models.user import User
from dao.attendance_dao import AttendanceDAO

attendance_bp = Blueprint('attendance', __name__)
attendance_service = AttendanceService()
attendance_dao = AttendanceDAO()

@attendance_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.employee:
        flash("You are not registered as an employee.", "danger")
        return redirect(url_for('dashboard.index'))

    try:
        attendance_service.process_check_in(user.employee.id)
        flash("Checked in successfully.", "success")
    except HRPortalBaseError as e:
        flash(str(e), "warning")
    except Exception as e:
        flash("An error occurred during check-in.", "danger")

    return redirect(url_for('dashboard.index'))

@attendance_bp.route('/check-out', methods=['POST'])
@jwt_required()
def check_out():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.employee:
        flash("You are not registered as an employee.", "danger")
        return redirect(url_for('dashboard.index'))

    try:
        attendance_service.process_check_out(user.employee.id)
        flash("Checked out successfully.", "success")
    except HRPortalBaseError as e:
        flash(str(e), "warning")
    except Exception as e:
        flash("An error occurred during check-out.", "danger")

    return redirect(url_for('dashboard.index'))

@attendance_bp.route('/my-logs', methods=['GET'])
@jwt_required()
def my_logs():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.employee:
        flash("You are not registered as an employee.", "danger")
        return redirect(url_for('dashboard.index'))

    # Fetching attendance records for the employee
    records = attendance_dao.get_by_employee_id(user.employee.id)
    return render_template('attendance/my_logs.html', records=records)
