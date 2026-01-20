from app import app, db, User, Note, ShareLink
from datetime import datetime, timezone, timedelta
import time

with app.app_context():
    print("=== 测试时区修复功能 ===")
    
    # 1. 获取测试用户和笔记
    user = User.query.filter_by(username='admin').first()
    note = Note.query.get(14)  # 确保这个笔记ID存在
    
    if not user:
        print("测试用户不存在")
        exit()
    
    if not note:
        print("测试笔记不存在")
        exit()
    
    print(f"用户: {user.username}")
    print(f"笔记: {note.title}")
    
    # 2. 创建分享链接 - 可编辑权限，1分钟过期
    print("\n2. 创建分享链接 (可编辑，1分钟过期)...")
    
    # 计算1分钟后的过期时间
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=1)
    
    # 生成token
    import uuid
    token = str(uuid.uuid4())
    
    # 创建分享链接
    link = ShareLink(
        note_id=note.id,
        token=token,
        permission='edit',
        expire_at=expire_time
    )
    
    db.session.add(link)
    db.session.commit()
    
    print(f"分享链接创建成功")
    print(f"Token: {token}")
    print(f"权限: {link.permission}")
    print(f"数据库中存储的过期时间(UTC): {link.expire_at}")
    print(f"当前时间(UTC): {datetime.now(timezone.utc)}")
    print(f"当前时间(本地时间): {datetime.now()}")
    
    # 3. 测试前端时间格式化逻辑
    print("\n3. 测试前端时间格式化逻辑...")
    
    # 模拟前端formatDate函数
    def format_date(date_string):
        if not date_string:
            return ''
        date = datetime.fromisoformat(date_string)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    # 模拟前端时区转换
    local_expire_time = link.expire_at.replace(tzinfo=timezone.utc).astimezone().replace(tzinfo=None)
    
    print(f"前端显示的过期时间(本地时间): {local_expire_time}")
    print(f"使用formatDate格式化后: {format_date(link.expire_at.isoformat())}")
    
    # 4. 创建另一个分享链接 - 1天过期
    print("\n4. 创建分享链接 (可编辑，1天过期)...")
    
    expire_time_1d = datetime.now(timezone.utc) + timedelta(days=1)
    token_1d = str(uuid.uuid4())
    
    link_1d = ShareLink(
        note_id=note.id,
        token=token_1d,
        permission='edit',
        expire_at=expire_time_1d
    )
    
    db.session.add(link_1d)
    db.session.commit()
    
    print(f"分享链接创建成功")
    print(f"Token: {token_1d}")
    print(f"权限: {link_1d.permission}")
    print(f"数据库中存储的过期时间(UTC): {link_1d.expire_at}")
    
    # 模拟前端时区转换
    local_expire_time_1d = link_1d.expire_at.replace(tzinfo=timezone.utc).astimezone().replace(tzinfo=None)
    
    print(f"前端显示的过期时间(本地时间): {local_expire_time_1d}")
    print(f"使用formatDate格式化后: {format_date(link_1d.expire_at.isoformat())}")
    
    # 5. 清理测试数据
    print("\n5. 清理测试数据...")
    
    db.session.delete(link)
    db.session.delete(link_1d)
    db.session.commit()
    
    print("\n=== 测试完成 ===")