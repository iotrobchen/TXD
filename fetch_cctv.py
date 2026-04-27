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

    # 2. 抓取資料 (現在權限已經是全開狀態了)
    # 我們搜尋名稱包含 '鳶山' 的所有監視器
    api_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=contains(CCTVName,'鳶山')&$format=JSON"
    
    print("權限已確認，正在撈取鳶山堰資料...")
    res = requests.get(api_url, headers=headers)
    res.raise_for_status()
    data = res.json()

    # 3. 儲存結果到 data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    if isinstance(data, list) and len(data) > 0:
        print(f"✅ 成功！已抓到 {len(data)} 筆鳶山堰影像資料。")
        for item in data:
            print(f" - 找到地點: {item.get('CCTVName')}")
    else:
        print("⚠️ 雖然有權限，但找不到名稱含『鳶山』的資料，請檢查 TDX 資料庫。")
        # 備用方案：如果名字沒中，可能是分類不同，改抓水利署全部試試
        backup_url = "https://tdx.transportdata.tw/api/basic/v2/Resources/CCTV?$filter=AuthorityCode eq 'WRA'&$format=JSON"
        data = requests.get(backup_url, headers=headers).json()
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ 已改為抓取水利署所有影像 (共 {len(data)} 筆)。")

except Exception as e:
    print(f"❌ 發生錯誤：{e}")
    exit(1)
