from app import app
from models import db, User

# 创建应用上下文
with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 检查是否已有管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        # 创建默认管理员用户
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('默认管理员用户创建成功：用户名=admin，密码=admin123')
    else:
        print('管理员用户已存在')
    
    print('数据库初始化完成')
