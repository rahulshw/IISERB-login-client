import argparse
import getpass
import re
import signal
import sys
import threading
from datetime import datetime

import requests

REFRESH_INTERVAL = 3600  # in seconds


global_magic_hash = None


def get_magic_hash():
    r = requests.get('http://www.gstatic.com/generate_204')
    hashes = re.findall('<input type="hidden" name="magic" value="(.+?)">', r.text)
    return hashes[0] if hashes else None


def logout(magic_hash):
    r = requests.get(f'https://gateway.iiserb.ac.in:1003/logout?{magic_hash}')
    print(f'you have successfully logged out. date: {datetime.now()}. magic hash: {magic_hash}')


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
        print(f'you are successfully logged in. date: {datetime.now()} magic hash: {magic_hash}')


def refresh_login(username, password, magic_hash=None):
    if not magic_hash:
        magic_hash = get_magic_hash()
        if not magic_hash:
            print('Looks like you are already logged in. Try running after sometime. ')
            return False
    else:
        logout(magic_hash)
        magic_hash = get_magic_hash()

    global global_magic_hash
    global_magic_hash = magic_hash
    r = send_login_request(username, password, magic_hash)

    timer = threading.Timer(REFRESH_INTERVAL, refresh_login, args=(username, password, magic_hash))
    timer.daemon = True
    timer.start()
    return True


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


def handle_interrupt(_, __):
    print('Keyboard Interrupt received. Logging out.', logout(global_magic_hash))
    sys.exit(0)


signal.signal(signal.SIGINT, handle_interrupt)

if __name__ == '__main__':
    username, password = get_credentials()
    if refresh_login(username, password):
        signal.pause()
    else:
        exit(1)

