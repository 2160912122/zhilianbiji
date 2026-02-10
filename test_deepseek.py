import os
import httpx
import json
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 获取API密钥
api_key = os.getenv('DEEPSEEK_API_KEY')
model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

if not api_key:
    print('未设置DEEPSEEK_API_KEY环境变量')
    exit(1)

print(f'使用API密钥: {api_key[:10]}...')
print(f'使用模型: {model}')

# 测试API连接
try:
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是专业的笔记生成助手，生成内容需逻辑连贯、重点突出，避免冗余。"},
            {"role": "user", "content": "请围绕'回归算法'生成一篇详细笔记，结构清晰（分点或分段），内容详实，适合保存为个人笔记。"}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    print('发送API请求...')
    response = httpx.post(url, headers=headers, json=data, timeout=30)
    print(f'响应状态码: {response.status_code}')
    print(f'响应头: {dict(response.headers)}')
    
    if response.status_code == 200:
        result = response.json()
        print('API调用成功！')
        print(f'响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}')
    else:
        print(f'API调用失败，状态码: {response.status_code}')
        print(f'错误信息: {response.text}')
        
except Exception as e:
    print(f'发生异常: {e}')
    import traceback
    traceback.print_exc()
