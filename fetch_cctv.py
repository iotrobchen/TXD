import requests
import json
import os

def run():
    try:
        # 1. 取得 Token (維持權限獲取，確保其他鏡頭也能更新)
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': os.environ.get('TDX_CLIENT_ID').strip(),
            'client_secret': os.environ.get('TDX_CLIENT_SECRET').strip()
        }
        auth_res = requests.post(auth_url, data=auth_data)
        token = auth_res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

        # 2. 抓取新北交通資料 (為了獲取其他三峽鏡頭)
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/NewTaipei?$format=JSON"
        res = requests.get(api_url, headers=headers)
        
        final_list = []
        
        # A. 【手動新增】你找到的鳶山關鍵鏡頭
        final_list.append({
            "Name": "鳶山堰旁 (中山路仁愛街口)",
            "URL": "https://atis.ntpc.gov.tw/ATIS/ShowFrame4CCTV/C000219",
            "Source": "手動鎖定"
        })

        # B. 【自動搜尋】其他三峽相關鏡頭
        if res.status_code == 200:
            items = res.json().get('CCTVs', [])
            for item in items:
                name = item.get('SurveillanceDescription', '')
                url = item.get('VideoStreamURL')
                # 避開重複的 C000219，並抓取其他三峽鏡頭
                if url and "三峽" in name and "C000219" not in url:
                    final_list.append({
                        "Name": name,
                        "URL": url,
                        "Source": "新北交通"
                    })

        # 3. 儲存
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
            
        print(f"成功！已加入精確鏡頭 C000219 並自動匹配 {len(final_list)-1} 個三峽鏡頭。")

    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    run()
