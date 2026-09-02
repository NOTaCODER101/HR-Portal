from flask import Flask, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
# pyrefly: ignore [missing-import]
from flask_jwt_extended import JWTManager
from settings import Config
from config.database import db

# Initialise JWT manager (stateless, no app bound yet)
jwt = JWTManager()
csrf = CSRFProtect()

def create_app(config_override: dict | None = None) -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    # ── Timedelta helpers (JWTManager reads these as timedelta objects) ──────
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        minutes=app.config.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 15)
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        days=app.config.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)
    )

    # ── Initialise extensions ────────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)

    # ── Blocklist callback (checks if a jti has been revoked on logout) ──────
    from dao.audit_log_dao import AuditLogDAO
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:  # type: ignore[return]
        """Return True if the token's jti is in the revocation blocklist."""
        from models.jwt_blocklist import JWTBlocklist
        jti = jwt_payload['jti']
        token = db.session.query(JWTBlocklist).filter_by(jti=jti).first()
        return token is not None

    # ── JWT web redirect handlers (HTML instead of JSON 401s) ────────────────
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        flash("You must be logged in to view that page.", "danger")
        return redirect(url_for('auth.login'))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        flash("Your session has expired. Please log in again.", "danger")
        return redirect(url_for('auth.login'))

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        flash("You have been logged out. Please log in again.", "info")
        return redirect(url_for('auth.login'))

    # ── Context Processor ────────────────────────────────────────────────────
    from utils.auth_utils import inject_current_user
    app.context_processor(inject_current_user)

    # ── Register Blueprints (Controllers) ────────────────────────────────────
    from controllers import register_blueprints
    register_blueprints(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=3000, debug=True)
