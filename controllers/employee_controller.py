"""
controllers/employee_controller.py
==================================
Employee directory, profile viewing, and onboarding.
"""
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import EmployeeService
from services.exceptions import HRPortalBaseError
from dao.employee_dao import EmployeeDAO
from dao.department_dao import DepartmentDAO
from dao.designation_dao import DesignationDAO
from dao.document_dao import DocumentDAO
from utils.auth_utils import role_required

employee_bp = Blueprint('employee', __name__)
employee_service = EmployeeService()
employee_dao = EmployeeDAO()
department_dao = DepartmentDAO()
designation_dao = DesignationDAO()
document_dao = DocumentDAO()

@employee_bp.route('/', methods=['GET'], endpoint='directory')
@employee_bp.route('/directory', methods=['GET'], endpoint='index')
@jwt_required()
def directory():
    page = int(request.args.get('page', 1))
    per_page = 20
    employees = employee_dao.get_all()
    return render_template('employee/directory.html', employees=employees)

@employee_bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def profile(employee_id):
    employee = employee_dao.get_by_id(employee_id)
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for('employee.directory'))
        
    documents = document_dao.get_by_employee(employee_id)
    return render_template('employee/profile.html', employee=employee, documents=documents)

@employee_bp.route('/onboard', methods=['GET', 'POST'], endpoint='onboard')
@employee_bp.route('/new', methods=['GET', 'POST'], endpoint='new_employee')
@jwt_required()
@role_required('HR Admin')
def onboard():
    if request.method == 'GET':
        from datetime import date
        departments = department_dao.get_all()
        designations = designation_dao.get_all()
        managers = employee_dao.get_all()
        return render_template('employee/onboard.html', departments=departments, designations=designations, managers=managers, today=date.today().isoformat())

    # Extract form data
    data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'role': request.form.get('role'),
        'phone_number': request.form.get('phone_number'),
        'date_of_birth': datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
        'date_of_joining': datetime.strptime(request.form.get('date_of_joining'), '%Y-%m-%d').date() if request.form.get('date_of_joining') else None,
        'department_id': int(request.form.get('department_id')) if request.form.get('department_id') else None,
        'designation_id': int(request.form.get('designation_id')) if request.form.get('designation_id') else None,
        'manager_id': int(request.form.get('manager_id')) if request.form.get('manager_id') else None,
    }

    hr_user_id = get_jwt_identity()

    try:
        new_emp = employee_service.onboard_employee(
            data=data,
            admin_user_id=hr_user_id
        )
        flash(f"Employee {new_emp.first_name} onboarded successfully.", "success")
        return redirect(url_for('employee.profile', employee_id=new_emp.id))
    except HRPortalBaseError as e:
        flash(str(e), "danger")
        return redirect(url_for('employee.onboard'))
    except Exception as e:
        import traceback
        flash(f"An error occurred during onboarding: {str(e)}", "danger")
        print(traceback.format_exc())  # Print full traceback to Flask console
        return redirect(url_for('employee.onboard'))

@employee_bp.route('/<int:employee_id>/edit', methods=['GET', 'POST'], endpoint='edit')
@employee_bp.route('/<int:employee_id>/edit_employee', methods=['GET', 'POST'], endpoint='edit_employee')
@jwt_required()
@role_required('HR Admin', 'Manager')
def edit(employee_id):
    employee = employee_dao.get_by_id(employee_id)
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for('employee.directory'))

    if request.method == 'GET':
        departments = department_dao.get_all()
        designations = designation_dao.get_all()
        managers = employee_dao.get_all()
        return render_template('employee/edit.html', employee=employee, departments=departments, designations=designations, managers=managers)

    # Update basic profile fields
    if employee:
        employee.first_name = request.form.get('first_name') or employee.first_name
        employee.last_name = request.form.get('last_name') or employee.last_name
        employee.email = request.form.get('email') or employee.email
        employee.phone_number = request.form.get('phone_number') or employee.phone_number
        if request.form.get('date_of_birth'):
            employee.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        if request.form.get('date_of_joining'):
            employee.date_of_joining = datetime.strptime(request.form.get('date_of_joining'), '%Y-%m-%d').date()
        if request.form.get('department_id'):
            employee.department_id = int(request.form.get('department_id'))
        if request.form.get('designation_id'):
            employee.designation_id = int(request.form.get('designation_id'))
        if request.form.get('manager_id'):
            employee.manager_id = int(request.form.get('manager_id'))
        from config.database import db
        db.session.commit()

    flash("Employee profile updated successfully.", "success")
    return redirect(url_for('employee.profile', employee_id=employee.id))
