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

    # 2. 修正後的絕對路徑：加入 /Basic/
    # TDX 的基礎資源 API 正確路徑通常包含 Basic
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Basic/Resources/CCTV?$filter=contains(CCTVName,'鳶山')&$format=JSON"
    
    headers = {'Authorization': f'Bearer {token}'}
    api_res = requests.get(api_url, headers=headers)
    
    # 如果還是 404，嘗試另一個極簡路徑
    if api_res.status_code == 404:
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'鳶山')&$format=JSON"
        api_res = requests.get(api_url, headers=headers)

    # 3. 儲存結果
    data = api_res.json()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    if api_res.status_code == 200 and len(data) > 0:
        print(f"成功！抓到資料了。名稱：{data[0].get('CCTVName')}")
    else:
        print(f"狀態碼：{api_res.status_code}，內容：{data}")
        exit(1)

except Exception as e:
    print(f"出現錯誤：{e}")
    exit(1)
