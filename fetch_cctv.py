import requests
import json
import os

def run():
    try:
        # 1. 取得 Access Token (確保使用新金鑰)
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': os.environ.get('TDX_CLIENT_ID').strip(),
            'client_secret': os.environ.get('TDX_CLIENT_SECRET').strip()
        }
        
        print("正在嘗試登入並取得 Token...")
        auth_res = requests.post(auth_url, data=auth_data)
        auth_res.raise_for_status()
        auth_data_json = auth_res.json()
        token = auth_data_json.get('access_token')
        
        print(f"成功！目前 Scope: {auth_data_json.get('scope')}")

        # 2. 根據 OAS 3.0 文件，請求新北市 CCTV 資料
        # 路徑: /v2/Road/Traffic/CCTV/City/NewTaipei
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # 使用 $filter 搜尋名稱包含 "鳶山" 的設備
        api_url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/NewTaipei?$filter=contains(CCTVName,'鳶山')&$format=JSON"
        
        print(f"正在請求 API: {api_url}")
        res = requests.get(api_url, headers=headers)
        
        if res.status_code == 200:
            raw_data = res.json()
            # 根據文件格式，資料在 'CCTVs' 欄位裡
            cctv_list = raw_data.get('CCTVs', [])
            
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(cctv_list, f, ensure_ascii=False, indent=4)
            
            print(f"✅ 大功告成！抓到 {len(cctv_list)} 筆鳶山堰相關影像。")
        else:
            print(f"❌ API 請求失敗，狀態碼: {res.status_code}")
            print(f"錯誤回應: {res.text}")
            # 儲存錯誤訊息以便除錯
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump({"error": "api_failed", "msg": res.text}, f)

    except Exception as e:
        print(f"🔥 腳本執行異常: {e}")
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"error": "crash", "msg": str(e)}, f)

if __name__ == "__main__":
    run()
