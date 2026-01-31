import os
from datetime import timedelta


class Config:
    # 基础密钥配置（保留原有）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 数据库配置（保留你的数据库账号密码，无需修改）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:304416720zgZG@localhost:3306/zhilianbiji?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # JWT配置（保留原有7天过期，密钥不变，适配权限拦截）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # 文件上传配置（保留原有，适配你的文件管理功能）
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # CORS配置（优化：允许凭证传递，适配前端带token请求）
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:8080']
    CORS_SUPPORTS_CREDENTIALS = True  # 新增：允许跨域请求带cookie/token

    # AI配置（保留原有）
    ZHIPUAI_API_KEY = os.environ.get('ZHIPUAI_API_KEY', '')
    ZHIPUAI_MODEL = os.environ.get('ZHIPUAI_MODEL', 'glm-4')


class DevelopmentConfig(Config):
    # 开发环境：调试模式开启，SQLALCHEMY打印SQL（方便调试）
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    # 生产环境：关闭调试，确保安全
    DEBUG = False
    # 生产环境建议从环境变量读取密钥，避免硬编码
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


class TestingConfig(Config):
    # 测试环境：使用内存数据库，避免影响真实数据
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置映射（保留原有，方便启动时指定环境）
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# -------------------------- 新增：便捷获取配置的方法（适配app.py） --------------------------
def get_config():
    """根据环境变量获取配置，默认使用开发环境"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config[env]