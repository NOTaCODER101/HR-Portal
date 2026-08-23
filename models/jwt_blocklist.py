from config.database import db
from datetime import datetime, timezone

class JWTBlocklist(db.Model):
    """
    Stores revoked JWT token identifiers (jti) to implement server-side logout.
    When a user logs out, their token's jti is saved here. The blocklist
    callback in app.py checks this table on every protected request.
    """
    __tablename__ = 'jwt_blocklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<JWTBlocklist jti={self.jti}>"
