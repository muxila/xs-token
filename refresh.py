import json, datetime, os, urllib.request
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = b'0c3ec10e32c2f9df'
DEVICE_ID = '03ed2a00da4a0721'
BASE = 'http://api.5wjqjape9vhl.com/xhsapi'

def aes_encrypt(data):
    return AES.new(AES_KEY, AES.MODE_ECB).encrypt(pad(data, 16))

def aes_decrypt(data):
    return unpad(AES.new(AES_KEY, AES.MODE_ECB).decrypt(data), 16)

def enc(obj):
    return aes_encrypt(json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))

def dec(b):
    return json.loads(aes_decrypt(b).decode('utf-8'))

def post(path, data_obj, token=''):
    body = {"data": data_obj, "deviceId": DEVICE_ID, "token": token}
    url = f"{BASE}/{path}"
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleDart/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17',
        'deviceType': 'android', 'version': '1.1.2', 'time': now,
        'deviceBrand': 'google', 'deviceModel': 'Pixel 9 Pro XL',
        'systemName': 'Android', 'systemVersion': '17',
        'Content-Type': 'application/octet-stream',
    }
    req = urllib.request.Request(url, data=enc(body), headers=headers, method='POST')
    return dec(urllib.request.urlopen(req, timeout=30).read())

def main():
    account = os.environ['ACCOUNT_NAME']
    password = os.environ['ACCOUNT_PASSWORD']
    si = post('system/info', {})
    tok = si['data']['token']
    guest = f"{tok['token']}_{tok['user_id']}"
    lj = post('user/findByAccount', {"account_name": account, "account_password": password, "type": "login"}, guest)
    if lj.get('status') != 'y':
        raise SystemExit(f"login failed: {lj}")
    d = lj['data']
    print(f"{d['token']}_{d['user_id']}")

if __name__ == '__main__':
    main()
