import requests
import io

def test_transcribe():
    # 先登录获取token
    login_url = "http://localhost:5000/api/login"
    login_data = {"username": "testuser", "password": "testpass"}
    
    try:
        login_response = requests.post(login_url, json=login_data)
        print(f"登录状态码: {login_response.status_code}")
        login_result = login_response.json()
        print(f"登录响应: {login_result}")
        
        if login_result.get('code') != 200:
            print("登录失败")
            return
        
        token = login_result['data']['token']
        print(f"获取到token: {token[:50]}...")
        
        # 测试语音转写接口
        transcribe_url = "http://localhost:5000/api/transcribe"
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个简单的测试音频数据（使用有效的WebM头）
        # 最小WebM文件头
        webm_header = b'\x1a\x45\xdf\xa3\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        files = {'audio': ('test.webm', io.BytesIO(webm_header), 'audio/webm')}
        
        print("\n开始测试语音转写接口...")
        response = requests.post(transcribe_url, headers=headers, files=files)
        print(f"转写状态码: {response.status_code}")
        print(f"转写响应: {response.text}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcribe()
