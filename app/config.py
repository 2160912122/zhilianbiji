import os
from dotenv import load_dotenv
import secrets

# 加载环境变量
load_dotenv()

class Settings:
    # 数据库配置
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "ftt20050308")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_NAME = os.getenv("DB_NAME", "notes")
    DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    # JWT配置（生成随机密钥，替代硬编码）
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))  # 32位随机字符串
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 120

settings = Settings()