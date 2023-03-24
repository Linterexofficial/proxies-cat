import requests
import json
from tqdm import tqdm
import time
import pyfiglet
from colorama import Fore, Style
from ipwhois import IPWhois
from prettytable import PrettyTable

def get_proxy_location(proxy):
    try:
        ip = proxy.split(':')[0]
        obj = IPWhois(ip)
        results = obj.lookup_rdap()
        location = f"{results['network']['remarks'][0]['description']}"
        return location
    except:
        return 'Unknown'

def test_and_locate_proxies_in_file(file_path):
    with open(file_path, 'r') as f:
        proxies = [line.strip() for line in f.readlines()]

    results = []
    with tqdm(total=len(proxies), desc='Scanning', bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Style.RESET_ALL)) as pbar:
        for proxy in proxies:
            url = 'https://www.google.com'
            protocol = None
            location = get_proxy_location(proxy)
            try:
                response = requests.get(url, proxies={'https': f'https://{proxy}'}, timeout=5)
                protocol = 'https'
            except requests.exceptions.RequestException:
                try:
                    response = requests.get(url, proxies={'http': f'http://{proxy}'}, timeout=5)
                    protocol = 'http'
                except requests.exceptions.RequestException:
                    try:
                        response = requests.get(url, proxies={'socks4': f'socks4://{proxy}'}, timeout=5)
                        protocol = 'socks4'
                    except requests.exceptions.RequestException:
                        try:
                            response = requests.get(url, proxies={'socks5': f'socks5://{proxy}'}, timeout=5)
                            protocol = 'socks5'
                        except requests.exceptions.RequestException:
                            pass

            results.append((proxy, location, protocol))
            pbar.update(1)
            time.sleep(0.1)

        # Display the results in a table
        table = PrettyTable()
        table.field_names = ['Proxy', 'Location', 'Protocol']
        for result in results:
            table.add_row(result)
        print(table)



