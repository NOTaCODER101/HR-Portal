import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'mysql+pymysql://root:1234@mysql-db:3306/hr_portal')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///hr_portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-JWT-Extended configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_TOKEN_LOCATION = ['cookies']           # Read JWT from cookies, not Authorization header
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 480      # Access token expires in 8 hours (office day)
    JWT_REFRESH_TOKEN_EXPIRES_DAYS = 30        # Refresh token expires in 30 days
    JWT_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # HTTPS only in prod
    JWT_COOKIE_HTTPONLY = True                 # JS cannot access the cookie (XSS protection)
    JWT_COOKIE_SAMESITE = 'Lax'               # CSRF protection
    JWT_COOKIE_CSRF_PROTECT = False           # Disabled to use Flask-WTF CSRF instead

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024      # 5 MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
