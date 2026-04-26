import requests
import json
import os

try:
    # 1. 取得 Access Token
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': os.environ.get('TDX_CLIENT_ID'),
        'client_secret': os.environ.get('TDX_CLIENT_SECRET')
    }
    auth_res = requests.post(auth_url, data=auth_data)
    auth_res.raise_for_status()
    token = auth_res.json().get('access_token')

    # 2. 呼叫 API (使用最保險的通用路徑)
    # 注意：這裡使用 Resources (複數) 並加上完整過濾條件
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'鳶山堰')&$format=JSON"
    
    headers = {'Authorization': f'Bearer {token}'}
    api_res = requests.get(api_url, headers=headers)
    
    # 檢查是否抓到 Resource Not Found
    result = api_res.json()
    if isinstance(result, dict) and "message" in result:
        print(f"API 錯誤：{result['message']}")
        # 如果複數不行，嘗試單數路徑
        api_url = api_url.replace("Resources", "Resource")
        api_res = requests.get(api_url, headers=headers)
        result = api_res.json()

    # 3. 儲存結果
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    if isinstance(result, list) and len(result) > 0:
        print(f"成功！抓到 {len(result)} 筆資料。")
    else:
        print("警告：雖然沒報錯，但沒抓到鳶山堰的資料。")
        exit(1)

except Exception as e:
    print(f"運行失敗：{e}")
    exit(1)
