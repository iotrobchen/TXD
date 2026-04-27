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

        # 2. 請求新北市所有 CCTV 資料 (不使用 $filter 以免語法錯誤)
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        # 根據你的文件，這是最標準的新北市路徑
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/NewTaipei?$format=JSON"
        
        print("正在抓取新北市完整 CCTV 清單...")
        res = requests.get(api_url, headers=headers)
        res.raise_for_status()
        
        full_data = res.json()
        cctv_list = full_data.get('CCTVs', [])
        
        # 3. 在 Python 內過濾關鍵字 "鳶山" 或 "三峽"
        # 這樣就不會觸發 TDX 的 OData 語法錯誤
        keywords = ['鳶山', '三峽']
        filtered_data = [
            item for item in cctv_list 
            if any(kw in item.get('RoadName', '') or kw in item.get('SurveillanceDescription', '') for kw in keywords)
        ]

        # 如果過濾後是空的，就存入前 5 筆當作測試，確保網頁有東西看
        output_data = filtered_data if filtered_data else cctv_list[:5]

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 成功！從 {len(cctv_list)} 筆資料中篩選出 {len(filtered_data)} 筆符合關鍵字的影像。")

    except Exception as e:
        print(f"🔥 錯誤: {e}")
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"error": "process_failed", "msg": str(e)}, f)

if __name__ == "__main__":
    run()
