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

        # 2. 嘗試「非 Basic」的直接路徑
        # 有時候帳號權限會被導向 v2 的直接分類而非 basic 分類
        urls = [
            "https://tdx.transportdata.tw/api/basic/v2/Road/CCTV/City/NewTaipei",
            "https://tdx.transportdata.tw/api/basic/v2/Water/CCTV/WRA"
        ]
        
        data = None
        for url in urls:
            print(f"嘗試路徑: {url}")
            res = requests.get(f"{url}?$top=1&$format=JSON", headers=headers)
            if res.status_code == 200:
                data = res.json()
                print("成功連線！")
                break
        
        if not data:
            data = {"error": "all_paths_failed", "last_res": res.text}

    except Exception as e:
        data = {"error": "crash", "msg": str(e)}

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
