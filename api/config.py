import os
from datetime import timedelta

class Config:
    """Application configuration class"""

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://inventory_user:password@localhost:5432/inventory_nova')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', JWT_SECRET_KEY)

    # CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

    # File Storage
    DATA_PATH = os.getenv('DATA_PATH', '/data')

    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
