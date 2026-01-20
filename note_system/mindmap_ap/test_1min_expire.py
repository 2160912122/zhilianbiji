import time
from datetime import datetime, timedelta, timezone

from app import Note, ShareLink, User, app, db

with app.app_context():
    print("=== 测试1分钟过期功能 ===")

    # 1. 获取测试用户和笔记
    user = User.query.filter_by(username="admin").first()
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
        note_id=note.id, token=token, permission="edit", expire_at=expire_time
    )

    db.session.add(link)
    db.session.commit()

    print(f"分享链接创建成功")
    print(f"Token: {token}")
    print(f"权限: {link.permission}")
    print(f"过期时间: {link.expire_at}")
    print(f"当前时间: {datetime.now(timezone.utc)}")

    # 3. 检查分享链接是否未过期
    print("\n3. 立即检查分享链接...")

    from app import get_share_by_token

    link_from_function, is_expired = get_share_by_token(token)

    if link_from_function:
        print(f"获取分享链接成功")
        print(f"权限: {link_from_function.permission}")
        print(f"是否过期: {is_expired}")

        if not is_expired:
            print("✅ 分享链接当前未过期（符合预期）")
        else:
            print("❌ 分享链接已过期（不符合预期）")

    # 4. 等待1分钟后再次检查
    print("\n4. 等待61秒后再次检查...")
    time.sleep(61)  # 等待61秒

    print(f"当前时间: {datetime.now(timezone.utc)}")

    link_from_function, is_expired = get_share_by_token(token)

    if link_from_function:
        print(f"获取分享链接成功")
        print(f"权限: {link_from_function.permission}")
        print(f"是否过期: {is_expired}")

        if is_expired:
            print("✅ 分享链接已过期（符合预期）")
        else:
            print("❌ 分享链接仍未过期（不符合预期）")

    # 5. 清理测试数据
    print("\n5. 清理测试数据...")
    db.session.delete(link)
    db.session.commit()

    print("\n=== 测试完成 ===")
