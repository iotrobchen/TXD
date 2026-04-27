import requests
import json
import os

def run():
    # 1. 取得 Token
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': os.environ.get('TDX_CLIENT_ID').strip(),
        'client_secret': os.environ.get('TDX_CLIENT_SECRET').strip()
    }
    
    try:
        auth_res = requests.post(auth_url, data=auth_data)
        token = auth_res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

        # 2. 探測清單 (涵蓋所有可能的鳶山堰存放路徑)
        paths = [
            {"name": "水利署-基礎", "url": "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/WRA"},
            {"name": "水利署-一般", "url": "https://tdx.transportdata.tw/api/v2/Water/CCTV/WRA"},
            {"name": "新北水利", "url": "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/City/NewTaipei"},
            {"name": "新北交通", "url": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/NewTaipei"}
        ]
        
        final_list = []
        diag_log = []

        for p in paths:
            print(f"探測中: {p['name']}...")
            res = requests.get(f"{p['url']}?$format=JSON", headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                items = data if isinstance(data, list) else data.get('CCTVs', [])
                
                found_count = 0
                for item in items:
                    name = item.get('CCTVName') or item.get('SurveillanceDescription') or item.get('RoadName', '')
                    url = item.get('VideoStreamURL') or item.get('VideoImageURL')
                    
                    # 同時搜 鳶山、三峽、水庫
                    if url and any(kw in str(name) for kw in ['鳶山', '三峽', '水庫']):
                        final_list.append({"Name": name, "URL": url, "Source": p['name']})
                        found_count += 1
                
                diag_log.append(f"{p['name']}: 成功 (找到 {found_count} 筆)")
            else:
                diag_log.append(f"{p['name']}: 失敗 ({res.status_code})")

        # 3. 儲存
        # 如果什麼都沒找到，就把診斷日誌存進去
        if not final_list:
            final_list = [{"Name": "診斷報告", "URL": "#", "Source": " | ".join(diag_log)}]

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"連線異常: {e}")

if __name__ == "__main__":
    run()
