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
auth_res = requests.post(auth_url, data=auth_data)
token = auth_res.json().get('access_token')

# 2. 呼叫 API 抓取鳶山堰影像 (透過名稱過濾)
# api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'鳶山堰')&$format=JSON"
api_url = "api_url = "https://tdx.transportdata.tw/api/basic/v2/Resource/CCTV?$filter=AuthorityCode%20eq%20'WRA'&$format=JSON""

headers = {'Authorization': f'Bearer {token}'}
api_res = requests.get(api_url, headers=headers)

# 3. 儲存結果
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(api_res.json(), f, ensure_ascii=False, indent=4)
