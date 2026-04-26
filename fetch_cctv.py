import requests
import json
import os

# 1. 取得 Access Token
auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': os.environ.get('TDX_CLIENT_ID'),
    'client_secret': os.environ.get('TDX_CLIENT_SECRET')
}
print(f"嘗試登入 ID: {auth_data['client_id'][:5]}***") # 只印出開頭，確保安全

auth_res = requests.post(auth_url, data=auth_data)
if auth_res.status_code != 200:
    print(f"登入失敗！狀態碼：{auth_res.status_code}")
    print(f"錯誤訊息：{auth_res.text}")
    exit(1)

token = auth_res.json().get('access_token')

# 2. 測試最基本的 API 網址
api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$top=1&$format=JSON"
headers = {'Authorization': f'Bearer {token}'}
api_res = requests.get(api_url, headers=headers)

print(f"API 請求狀態碼：{api_res.status_code}")
print(f"API 完整回傳內容：{api_res.text}") # 這裡會揭開真相！

# 儲存
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(api_res.text)

if api_res.status_code != 200:
    exit(1)
