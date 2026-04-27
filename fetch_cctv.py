import requests
import json
import os

def run():
    try:
        # 1. 取得 Token
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': os.environ.get('TDX_CLIENT_ID').strip(),
            'client_secret': os.environ.get('TDX_CLIENT_SECRET').strip()
        }
        auth_res = requests.post(auth_url, data=auth_data)
        token = auth_res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

        # 2. 定義來源
        urls = {
            "水利署": "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/WRA?$format=JSON",
            "新北市": "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/NewTaipei?$format=JSON"
        }
        
        final_list = []
        keywords = ['鳶山', '三峽']

        for source_name, url in urls.items():
            print(f"正在抓取 {source_name}...")
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                raw = res.json()
                # 水利署格式是直接 list，道路格式在 'CCTVs'
                items = raw if isinstance(raw, list) else raw.get('CCTVs', [])
                
                for item in items:
                    # 取得名稱 (試過所有可能的欄位)
                    name = item.get('CCTVName') or item.get('SurveillanceDescription') or item.get('RoadName') or "未命名設備"
                    # 取得網址
                    link = item.get('VideoStreamURL') or item.get('VideoImageURL')
                    
                    # 關鍵字篩選
                    if any(kw in str(name) for kw in keywords):
                        final_list.append({
                            "Name": name,
                            "URL": link,
                            "Source": source_name
                        })

        # 3. 儲存
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        print(f"成功存入 {len(final_list)} 筆資料。")

    except Exception as e:
        print(f"錯誤: {e}")
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump([{"Name": "錯誤", "URL": "#", "Source": str(e)}], f)

if __name__ == "__main__":
    run()
