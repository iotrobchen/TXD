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
    headers = {'Authorization': f'Bearer {token}'}

    # 2. 嘗試抓取鳶山堰資料
    # 嘗試三個可能的關鍵字：'鳶山', '鳶山堰', '三峽'
    keywords = ['鳶山', '鳶山堰', '三峽']
    data = []
    
    for kw in keywords:
        api_url = f"https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'{kw}')&$format=JSON"
        print(f"嘗試關鍵字: {kw}")
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            temp_data = res.json()
            if isinstance(temp_data, list) and len(temp_data) > 0:
                data.extend(temp_data)
                print(f" -> 找到 {len(temp_data)} 筆資料")

    # 如果還是空的，抓取水利署所有 CCTV (這是最後的大絕招)
    if not data:
        print("關鍵字搜尋失敗，嘗試抓取水利署 (WRA) 全所有資料...")
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=AuthorityCode eq 'WRA'&$format=JSON"
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            data = res.json()

    # 3. 儲存結果
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    if isinstance(data, list) and len(data) > 0:
        print(f"🎉 成功！最終存入 {len(data)} 筆資料到 data.json")
    else:
        print(f"❌ 警告：所有搜尋方式都失敗。最後一次 API 狀態碼: {res.status_code}")
        print(f"回傳內容: {res.text}")
        exit(1)

except Exception as e:
    print(f"🔥 執行出錯：{e}")
    exit(1)
