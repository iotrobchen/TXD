import requests
import json
import os

def run():
    try:
        # 1. 取得 Access Token
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': os.environ.get('TDX_CLIENT_ID').strip(),
            'client_secret': os.environ.get('TDX_CLIENT_SECRET').strip()
        }
        auth_res = requests.post(auth_url, data=auth_data)
        auth_res.raise_for_status()
        token = auth_res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

        # 2. 定義要抓取的多個來源
        # 來源 A: 水利署 (最可能有鳶山堰)
        # 來源 B: 新北市道路 (我們之前抓的)
        target_urls = [
            "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/WRA?$format=JSON",
            "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/NewTaipei?$format=JSON"
        ]
        
        all_cctvs = []
        for url in target_urls:
            print(f"嘗試抓取來源: {url}")
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                # 注意：不同 API 的 JSON 結構可能略有不同
                data = res.json()
                # 水利署格式通常直接是 list，道路格式在 'CCTVs' 裡
                items = data if isinstance(data, list) else data.get('CCTVs', [])
                all_cctvs.extend(items)

        # 3. 關鍵字篩選 (包含 鳶山, 鳶山堰, 三峽)
        keywords = ['鳶山', '三峽']
        filtered_data = []
        
        for item in all_cctvs:
            # 檢查所有可能的名稱欄位
            name_fields = [
                str(item.get('CCTVName', '')), 
                str(item.get('SurveillanceDescription', '')), 
                str(item.get('RoadName', ''))
            ]
            combined_text = " ".join(name_fields)
            
            if any(kw in combined_text for kw in keywords):
                # 統一格式：確保都有 VideoStreamURL
                # 水利署的欄位可能叫 VideoStreamURL 或其它，我們做個相容性處理
                url = item.get('VideoStreamURL') or item.get('VideoImageURL')
                if url:
                    filtered_data.append({
                        "Name": item.get('CCTVName') or item.get('SurveillanceDescription') or "未命名設備",
                        "URL": url,
                        "Source": "WRA" if "Water" in str(item) else "Road"
                    })

        # 4. 儲存結果
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 完成！共找到 {len(filtered_data)} 筆鳶山相關影像。")

    except Exception as e:
        print(f"🔥 錯誤: {e}")
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump([], f)

if __name__ == "__main__":
    run()
