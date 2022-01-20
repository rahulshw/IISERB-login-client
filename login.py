import argparse
import getpass
import re
import threading

import requests

REFRESH_INTERVAL = 5  # in seconds


def get_magic_hash():
    r = requests.get('https://www.google.com', verify=False)
    hashes = re.findall('<input type="hidden" name="magic" value="(.+?)">', r.text)
    return hashes[0] if hashes else None


def logout(magic_hash):
    r = requests.get(f'https://gateway.iiserb.ac.in:1003/logout?{magic_hash}')
    print(f'you have successfully logged out. magic hash: {magic_hash}')


def send_login_request(username, password, magic_hash):
    payload = {
        "4Tredir": "https://google.com",
        "magic": magic_hash,
        "username": username,
        "password": password
    }
    headers = {
        "Content-type": "application/json",
        "Referer": f"https://gateway.iiserb.ac.in:1003/fgtauth?{magic_hash}",

    }
    r = requests.post('https://gateway.iiserb.ac.in:1003', headers=headers, data=payload)
    if r.status_code == 200:
        print(f'you are successfully logged in. magic hash: {magic_hash}')


def refresh_login(username, password, magic_hash=None):
    if not magic_hash:
        magic_hash = get_magic_hash()
        if not magic_hash:
            print('Looks like you are already logged in. Try running after sometime. ')
            return
    else:
        logout(magic_hash)
        magic_hash = get_magic_hash()

    r = send_login_request(username, password, magic_hash)

    timer = threading.Timer(REFRESH_INTERVAL, refresh_login, args=(username, password, magic_hash))
    timer.daemon = True
    timer.start()


def get_credentials():
    parser = argparse.ArgumentParser(description='IISERB login client for internet access.')
    parser.add_argument('--username', help='LDAPP username', required=False)
    parser.add_argument('--password', help='LDAPP password', required=False)

    args = parser.parse_args()
    username, password = args.username, args.password
    if not username:
        username = input('Username: ')
    if not password:
        password = getpass.getpass('Password: ')
    return username, password


if __name__ == '__main__':
    username, password = get_credentials()
    refresh_login(username, password)
