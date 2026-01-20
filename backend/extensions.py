from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# 创建扩展实例
db = SQLAlchemy()
cors = CORS()
bcrypt = Bcrypt()
jwt = JWTManager()