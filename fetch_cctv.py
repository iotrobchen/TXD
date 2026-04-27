import requests
import json
import os

def run():
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

        # 2. 改用「新北市」的路徑，這通常包含轄區內的所有 CCTV
        # 既然你在官網看到了縣市 CCTV，這條路徑權限極高
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/CCTV/City/NewTaipei?$filter=contains(CCTVName,'鳶山')&$format=JSON"
        
        print(f"正在請求新北市路徑...")
        res = requests.get(api_url, headers=headers)
        
        # 3. 檢查結果
        if res.status_code == 200:
            data = res.json()
            # 如果新北市撈不到，嘗試「水利署 WRA」路徑
            if not data:
                print("新北市路徑無資料，嘗試水利署專屬路徑...")
                wra_url = "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/WRA?$format=JSON"
                res = requests.get(wra_url, headers=headers)
                data = res.json()
        else:
            data = {"error": "api_failed", "msg": res.text, "path": api_url}

    except Exception as e:
        data = {"error": "crash", "msg": str(e)}

    # 儲存
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("存檔完成。")

if __name__ == "__main__":
    run()
