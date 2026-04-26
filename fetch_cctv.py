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

    # 2. 呼叫 API - 這次使用「水利署專屬」的 CCTV 路徑
    # 這個路徑在 TDX V2 中是最準確的
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/WRA?$filter=contains(CCTVName,'鳶山堰')&$format=JSON"
    
    headers = {'Authorization': f'Bearer {token}'}
    api_res = requests.get(api_url, headers=headers)
    
    # 檢查是否還是找不到資源
    if api_res.status_code == 404:
        # 如果水利署專屬路徑不行，改回通用路徑 (Resources 複數)
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'鳶山堰')&$format=JSON"
        api_res = requests.get(api_url, headers=headers)

    result = api_res.json()

    # 3. 儲存結果
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    # 檢查抓到的資料數量
    if isinstance(result, list) and len(result) > 0:
        print(f"成功！抓到 {len(result)} 筆資料，名稱：{result[0].get('CCTVName')}")
    else:
        print("警告：連線成功但篩選不到『鳶山堰』，請檢查關鍵字。")
        print(f"API 回傳內容：{result}")
        exit(1)

except Exception as e:
    print(f"運行失敗：{e}")
    exit(1)
