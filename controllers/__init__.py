"""
controllers/__init__.py
=======================
Registers all blueprints to the main Flask app.
"""
from flask import Flask

def register_blueprints(app: Flask) -> None:
    from .auth_controller import auth_bp
    from .dashboard_controller import dashboard_bp
    from .employee_controller import employee_bp
    from .attendance_controller import attendance_bp
    from .leave_controller import leave_bp
    from .holiday_controller import holiday_bp
    from .document_controller import document_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employee_bp, url_prefix='/employees')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(leave_bp, url_prefix='/leaves')
    app.register_blueprint(holiday_bp, url_prefix='/holidays')
    app.register_blueprint(document_bp, url_prefix='/documents')
