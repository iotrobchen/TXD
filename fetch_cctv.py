import requests
import json
import os

def fetch_data():
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
    headers = {'Authorization': f'Bearer {token}'}

    # 2. 定義三種可能的 TDX 基礎影像路徑
    # 我們從「最廣義」到「最精確」都試一遍
    urls = [
        "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV",
        "https://tdx.transportdata.tw/api/basic/v2/Road/CCTV/WRA", # 水利署專屬
        "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV"
    ]
    
    for url in urls:
        full_url = f"{url}?$filter=contains(CCTVName,'鳶山')&$format=JSON"
        print(f"正在嘗試路徑: {url}")
        res = requests.get(full_url, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            if data:
                print(f"成功！在 {url} 找到資料")
                return data
    
    print("所有已知路徑皆失效。")
    return {"error": "All paths failed", "last_status": res.status_code}

try:
    result = fetch_data()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    if isinstance(result, list):
        print(f"完成！抓到 {len(result)} 筆資料。")
    else:
        exit(1)

except Exception as e:
    print(f"異常結束：{e}")
    exit(1)
