from typing import Optional
from config.database import db
from models.user import User
from dao.base_dao import BaseDAO

class UserDAO(BaseDAO):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by their unique username."""
        return db.session.query(User).filter(User.username == username).first()

    def update_password(self, user_id: int, new_password_hash: str) -> Optional[User]:
        """Update a user's password hash."""
        user = self.get_by_id(user_id)
        if user:
            user.password_hash = new_password_hash
        return user

    def set_active_status(self, user_id: int, is_active: bool) -> Optional[User]:
        """Activate or deactivate a user account."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = is_active
        return user
