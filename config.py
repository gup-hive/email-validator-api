"""
Email Validator API Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max CSV upload
    RATE_LIMIT = 100  # requests per minute
    PRICING_PER_EMAIL = 0.001
    PRICING_MONTHLY_50K = 29.0
    SMTP_TIMEOUT = 10  # seconds
    MX_TIMEOUT = 5  # seconds

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
