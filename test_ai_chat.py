import requests
import json

# 测试AI聊天接口
def test_ai_chat():
    # 获取JWT令牌
    login_url = 'http://localhost:5000/api/login'
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("正在登录...")
    login_response = requests.post(login_url, json=login_data)
    print(f"登录响应状态码: {login_response.status_code}")
    print(f"登录响应内容: {login_response.json()}")
    
    if login_response.status_code == 200:
        token = login_response.json().get('data', {}).get('token')
        if token:
            # 调用AI聊天接口
            ai_url = 'http://localhost:5000/api/ai/chat'
            ai_data = {
                'messages': [
                    {'role': 'user', 'content': '生成关于Python基础的笔记'}
                ]
            }
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("\n正在调用AI聊天接口...")
            ai_response = requests.post(ai_url, json=ai_data, headers=headers)
            print(f"AI聊天响应状态码: {ai_response.status_code}")
            print(f"AI聊天响应内容: {ai_response.json()}")
        else:
            print("未获取到JWT令牌")
    else:
        print("登录失败")

if __name__ == "__main__":
    test_ai_chat()
