"""
controllers/auth_controller.py
==============================
Handles login, logout, and password changes.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_wtf.csrf import generate_csrf

from services import AuthService
from services.exceptions import HRPortalBaseError

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        response = redirect(url_for('dashboard.index'))
        auth_service.login_user(username or "", password or "", response)
        flash("Successfully logged in.", "success")
        return response
    except HRPortalBaseError as e:
        flash(str(e), "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        response = redirect(url_for('auth.login'))
        jti = get_jwt_identity() # Actually we need the JTI to blocklist it. The service expects `jti`.
        from flask_jwt_extended import get_jwt
        jti = get_jwt()['jti']
        auth_service.logout_user(response)
        flash("You have been logged out.", "info")
        return response
    except Exception as e:
        flash("An error occurred during logout.", "danger")
        return redirect(url_for('dashboard.index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@jwt_required()
def change_password():
    if request.method == 'GET':
        return render_template('auth/change_password.html')

    user_id = get_jwt_identity()
    old_password = request.form.get('old_password') or ""
    new_password = request.form.get('new_password') or ""
    confirm_password = request.form.get('confirm_password') or ""

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('auth.change_password'))

    try:
        auth_service.change_password(user_id, old_password, new_password)
        flash("Password successfully updated.", "success")
        return redirect(url_for('dashboard.index'))
    except HRPortalBaseError as e:
        flash(str(e), "danger")
        return redirect(url_for('auth.change_password'))
