import os
from datetime import timedelta


class Config:
    # 基础密钥配置（支持环境变量）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # MySQL数据库配置（本地MySQL）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:123456@localhost:3306/zhilianbiji?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # JWT配置（支持环境变量）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # CORS配置
    CORS_ORIGINS = [
        'http://47.93.192.247',
        'http://localhost:5173',
        'http://localhost:5174'
    ]
    CORS_SUPPORTS_CREDENTIALS = True


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


# 配置映射
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}


def get_config():
    """根据环境变量获取配置，默认使用开发环境"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config[env]