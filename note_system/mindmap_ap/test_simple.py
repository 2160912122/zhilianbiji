from app import app, db, ShareLink
from datetime import datetime, timezone, timedelta

with app.app_context():
    print("=== 简单测试分享链接功能 ===")
    
    # 创建测试分享链接
    import uuid
    token = str(uuid.uuid4())
    expire_time = datetime.now(timezone.utc) + timedelta(days=1)
    
    link = ShareLink(
        note_id=14,
        token=token,
        permission='edit',
        expire_at=expire_time
    )
    
    db.session.add(link)
    db.session.commit()
    
    print(f"创建分享链接: token={token}, permission={link.permission}, expire_at={link.expire_at}")
    
    # 测试get_share_by_token函数
    from app import get_share_by_token
    
    link_from_function, is_expired = get_share_by_token(token)
    
    if link_from_function:
        print(f"\nget_share_by_token结果:")
        print(f"permission={link_from_function.permission}")
        print(f"expire_at={link_from_function.expire_at}")
        print(f"is_expired={is_expired}")
        
        # 检查权限是否正确传递
        if link_from_function.permission == 'edit':
            print("✅ 权限正确传递")
        else:
            print("❌ 权限传递错误")
            
        # 检查过期时间是否正确
        if link_from_function.expire_at:
            print("✅ 过期时间已设置")
        else:
            print("❌ 过期时间未设置")
    
    # 清理测试数据
    db.session.delete(link)
    db.session.commit()
    print("\n测试完成")