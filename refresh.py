import json, datetime, os, urllib.request, sys
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

def post(path, data_obj, token='', base=None):
    base = base or BASE
    body = {"data": data_obj, "deviceId": DEVICE_ID, "token": token}
    url = f"{base}/{path}"
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleDart/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17',
        'deviceType': 'android', 'version': '1.1.2', 'time': now,
        'deviceBrand': 'google', 'deviceModel': 'Pixel 9 Pro XL',
        'systemName': 'Android', 'systemVersion': '17',
        'Content-Type': 'application/octet-stream',
    }
    req = urllib.request.Request(url, data=enc(body), headers=headers, method='POST')
    raw = urllib.request.urlopen(req, timeout=30).read()
    print(f"[debug] {path} len={len(raw)} head_hex={raw[:32].hex()}", file=sys.stderr)
    return json.loads(aes_decrypt(raw).decode('utf-8'))

def main():
    account = os.environ['ACCOUNT_NAME']
    password = os.environ['ACCOUNT_PASSWORD']

    si = post('system/info', {})
    tok = si['data']['token']
    guest = f"{tok['token']}_{tok['user_id']}"
    domains = si['data'].get('domains', []) or []

    bases = []
    for d in domains:
        d = d.rstrip('/')
        bases.append(f"{d}/xhsapi")
    bases.append(BASE)

    last_err = None
    for base in bases:
        try:
            lj = post('user/findByAccount', {
                "account_name": account,
                "account_password": password,
                "type": "login",
            }, guest, base)
            if lj.get('status') == 'y':
                d = lj['data']
                print(f"{d['token']}_{d['user_id']}")
                return
            last_err = lj
        except Exception as e:
            last_err = e
            print(f"[debug] login failed on {base}: {e}", file=sys.stderr)

    raise SystemExit(f"login failed on all domains: {last_err}")

main()
