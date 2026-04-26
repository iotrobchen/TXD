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

    # 2. 呼叫 API - 使用基礎 API V2 最標準的路徑
    # 這次我們把關鍵字縮短，只找「鳶山」，避免因為名稱內的空格或全形符號導致失敗
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'鳶山')&$format=JSON"
    
    headers = {'Authorization': f'Bearer {token}'}
    api_res = requests.get(api_url, headers=headers)
    
    # 檢查是否抓到資料
    data = api_res.json()

    # 3. 儲存結果
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    if isinstance(data, list) and len(data) > 0:
        print(f"成功！抓到 {len(data)} 筆資料，第一筆是：{data[0].get('CCTVName')}")
    else:
        print(f"警告：API 回傳成功但內容為空或格式錯誤。回傳內容：{data}")
        exit(1)

except Exception as e:
    print(f"運行失敗：{e}")
    exit(1)
