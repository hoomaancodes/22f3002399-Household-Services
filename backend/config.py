import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = 'your-secret-key-here'  # Change this in production!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///household_services.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = 'jwt-secret-key'  # Change this in production!
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    
    # Admin credentials
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'admin_password'  # Change this in production!
    
    # CORS configuration
    CORS_HEADERS = 'Content-Type'
