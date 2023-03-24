import requests
import time
from itertools import cycle

def detect_chaining(proxies):
    proxy_chain = False
    for proxy in proxies:
        try:
            response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=5)
            if 'client-ip' in response.text:
                proxy_chain = True
        except:
            pass
    if proxy_chain:
        print('Proxy chaining detected')
    else:
        print('No proxy chaining detected')