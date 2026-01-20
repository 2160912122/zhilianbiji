from datetime import datetime, timedelta, timezone

from app import Note, ShareLink, User, app, db

with app.app_context():
    print("=== 直接测试分享链接功能 ===")

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

    # 2. 创建分享链接 - 可编辑权限，1天过期
    print("\n2. 创建分享链接 (可编辑，1天过期)...")

    # 计算1天后的过期时间
    expire_time = datetime.now(timezone.utc) + timedelta(days=1)

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
    print(f"过期时间类型: {type(link.expire_at)}")

    # 3. 检查分享链接
    print("\n3. 检查分享链接...")

    # 从数据库获取分享链接
    saved_link = ShareLink.query.filter_by(token=token).first()

    if saved_link:
        print(f"从数据库获取分享链接成功")
        print(f"权限: {saved_link.permission}")
        print(f"过期时间: {saved_link.expire_at}")
        print(f"过期时间类型: {type(saved_link.expire_at)}")

        # 检查权限是否正确
        if saved_link.permission == "edit":
            print("✅ 权限设置正确")
        else:
            print("❌ 权限设置不正确")

        # 检查过期时间是否正确
        if (
            saved_link.expire_at
            and abs((saved_link.expire_at - expire_time).total_seconds()) < 1
        ):
            print("✅ 过期时间设置正确")
        else:
            print("❌ 过期时间设置不正确")

    # 4. 测试get_share_by_token函数
    print("\n4. 测试get_share_by_token函数...")

    from app import get_share_by_token

    try:
        link_from_function, is_expired = get_share_by_token(token)
        print(f"获取分享链接成功")
        print(f"权限: {link_from_function.permission}")
        print(f"过期时间: {link_from_function.expire_at}")
        print(f"是否过期: {is_expired}")

        if link_from_function.permission == "edit":
            print("✅ 权限获取正确")
        else:
            print("❌ 权限获取不正确")

        if not is_expired:
            print("✅ 过期状态检查正确")
        else:
            print("❌ 过期状态检查不正确")

    except Exception as e:
        print(f"获取分享链接失败: {e}")

    print("\n=== 测试完成 ===")
