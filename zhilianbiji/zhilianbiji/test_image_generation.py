import requests
import json

# 测试图像生成API
url = 'http://localhost:5000/api/ai/generate-image'
headers = {'Content-Type': 'application/json'}
data = {'prompt': '一只可爱的小猫'}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"请求失败: {str(e)}")
