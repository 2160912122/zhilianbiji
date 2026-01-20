import requests
import json
from datetime import datetime, timedelta

# 测试配置
BASE_URL = 'http://localhost:5000'
USERNAME = 'admin'
PASSWORD = 'admin123'

# 第一步：登录获取token
def login():
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    response = requests.post(f'{BASE_URL}/api/login', json=login_data)
    if response.status_code == 200:
        return response.json().get('token')
    else:
        print(f"登录失败: {response.status_code}")
        return None

# 第二步：创建测试笔记
def create_test_note(token):
    note_data = {
        'title': '测试分享笔记',
        'content': '<p>这是一个测试分享笔记的内容</p>',
        'type': 'richtext'
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{BASE_URL}/api/notes', json=note_data, headers=headers)
    if response.status_code == 201:
        return response.json().get('id')
    else:
        print(f"创建笔记失败: {response.status_code}, {response.text}")
        return None

# 第三步：创建分享链接
def create_share_link(token, note_id, expire_time=3600):
    share_data = {
        'note_id': note_id,
        'permission': 'view',
        'expire_time': expire_time
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{BASE_URL}/api/share', json=share_data, headers=headers)
    if response.status_code == 200:
        return response.json().get('token')
    else:
        print(f"创建分享链接失败: {response.status_code}, {response.text}")
        return None

# 第四步：访问分享页面
def check_share_page(token):
    response = requests.get(f'{BASE_URL}/share/{token}')
    if response.status_code == 200:
        content = response.text
        print("分享页面访问成功！")
        
        # 检查页面中是否包含正确的时间格式
        if '将在 2026-01-16 10:' in content:
            print("✅ 成功：分享页面显示的过期时间已转换为本地时间")
        elif '将在 2026-01-16 02:' in content:
            print("❌ 失败：分享页面显示的过期时间仍是UTC时间")
        else:
            print("❓ 警告：未找到预期的时间格式")
            
        return True
    else:
        print(f"访问分享页面失败: {response.status_code}")
        return False

# 主测试流程
def main():
    print("=== 分享页面过期时间时区测试 ===")
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    print("✅ 登录成功")
    
    # 2. 创建测试笔记
    note_id = create_test_note(token)
    if not note_id:
        return
    
    print(f"✅ 创建测试笔记成功，ID: {note_id}")
    
    # 3. 创建分享链接（1分钟后过期）
    share_token = create_share_link(token, note_id, expire_time=60)
    if not share_token:
        return
    
    print(f"✅ 创建分享链接成功，Token: {share_token}")
    
    # 4. 访问分享页面并检查时间显示
    check_share_page(share_token)

if __name__ == '__main__':
    main()