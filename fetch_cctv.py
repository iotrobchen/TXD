import requests
import os

auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': os.environ.get('TDX_CLIENT_ID'),
    'client_secret': os.environ.get('TDX_CLIENT_SECRET')
}

auth_res = requests.post(auth_url, data=auth_data)
token_data = auth_res.json()

if "access_token" in token_data:
    print("--- 登入成功 ---")
    # 解碼 Token 雖然比較複雜，但我們可以看回傳的 scope
    print(f"你的帳號權限範圍 (Scope): {token_data.get('scope')}")
else:
    print("登入失敗，請檢查金鑰。")
