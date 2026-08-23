"""
controllers/holiday_controller.py
=================================
View and manage corporate holidays.
"""
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import HolidayService
from services.exceptions import HRPortalBaseError
from dao.holiday_dao import HolidayDAO
from utils.auth_utils import role_required

holiday_bp = Blueprint('holiday', __name__)
holiday_service = HolidayService()
holiday_dao = HolidayDAO()

@holiday_bp.route('/', methods=['GET'], endpoint='calendar')
@holiday_bp.route('/calendar', methods=['GET'], endpoint='index')
@jwt_required()
def calendar():
    from sqlalchemy import asc
    holidays = holiday_dao.get_all_ordered()
    return render_template('holiday/calendar.html', holidays=holidays)

@holiday_bp.route('/add', methods=['POST'])
@jwt_required()
@role_required('HR Admin')
def add():
    name = request.form.get('name')
    date_str = request.form.get('date')
    description = request.form.get('description', '')
    user_id = get_jwt_identity()

    date_string = request.form.get('date') or ""
    try:
        holiday_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        holiday_service.add_holiday(
            name=request.form.get('name') or "",
            holiday_date=holiday_date,
            description=request.form.get('description') or "",
            admin_user_id=user_id
        )
        flash(f"Holiday '{name}' added successfully.", "success")
    except ValueError:
        flash("Invalid date format. Use YYYY-MM-DD.", "danger")
    except HRPortalBaseError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash("An error occurred while adding the holiday.", "danger")

    return redirect(url_for('holiday.calendar'))

@holiday_bp.route('/<int:holiday_id>/delete', methods=['POST'])
@jwt_required()
@role_required('HR Admin')
def delete(holiday_id):
    user_id = get_jwt_identity()

    try:
        holiday_service.remove_holiday(holiday_id, user_id)
        flash("Holiday deleted successfully.", "success")
    except HRPortalBaseError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash("An error occurred while deleting the holiday.", "danger")

    return redirect(url_for('holiday.calendar'))


@holiday_bp.route('/<int:holiday_id>/edit', methods=['POST'])
@jwt_required()
@role_required('HR Admin')
def edit(holiday_id):
    user_id = get_jwt_identity()
    name = request.form.get('name', '').strip()
    date_str = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()

    if not name or not date_str:
        flash("Holiday name and date are required.", "danger")
        return redirect(url_for('holiday.calendar'))

    try:
        holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        holiday_service.update_holiday(
            holiday_id=holiday_id,
            name=name,
            holiday_date=holiday_date,
            description=description or None,
            admin_user_id=user_id,
        )
        flash(f"Holiday '{name}' updated successfully.", "success")
    except ValueError:
        flash("Invalid date format.", "danger")
    except HRPortalBaseError as e:
        flash(str(e), "danger")
    except Exception:
        flash("An error occurred while updating the holiday.", "danger")

    return redirect(url_for('holiday.calendar'))

