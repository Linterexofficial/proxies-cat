import requests
from prettytable import PrettyTable
import socks
import socket

def load_proxies_from_file(file_path):
    proxies = []
    with open(file_path, "r") as file:
        for line in file:
            proxy = line.strip()
            if proxy:
                proxies.append(proxy)
    return proxies

def test_proxiess(proxies):
    working_proxies = []
    non_working_proxies = []
    results = PrettyTable()
    results.field_names = ["Proxy", "Protocol", "Status"]
    for proxy in proxies:
        parts = proxy.split(":")
        ip = parts[0]
        port = int(parts[1])
        protocol = parts[2].lower() if len(parts) > 2 else None

        if protocol == "http" or protocol == "https":
            try:
                proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
                response = requests.get("https://www.google.com", proxies=proxies, timeout=5)
                if response.status_code == 200:
                    working_proxies.append(proxy)
                    results.add_row([proxy, protocol.upper() if protocol else "HTTP(S)", "Working"])
                else:
                    non_working_proxies.append(proxy)
                    results.add_row([proxy, protocol.upper() if protocol else "HTTP(S)", "Not Working"])
            except:
                non_working_proxies.append(proxy)
                results.add_row([proxy, protocol.upper() if protocol else "HTTP(S)", "Not Working"])
        
        elif protocol == "socks4":
            try:
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, ip, port)
                socket.socket = socks.socksocket
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('www.google.com', 80))
                working_proxies.append(proxy)
                results.add_row([proxy, "SOCKS4", "Working"])
            except:
                non_working_proxies.append(proxy)
                results.add_row([proxy, "SOCKS4", "Not Working"])

        elif protocol == "socks5":
            try:
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port)
                socket.socket = socks.socksocket
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('www.google.com', 80))
                working_proxies.append(proxy)
                results.add_row([proxy, "SOCKS5", "Working"])
            except:
                non_working_proxies.append(proxy)
                results.add_row([proxy, "SOCKS5", "Not Working"])
        
        else:
            try:
                proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
                response = requests.get("https://www.google.com", proxies=proxies, timeout=5)
                if response.status_code == 200:
                    working_proxies.append(proxy)
                    results.add_row([proxy, "Unknown", "Working"])
                else:
                    non_working_proxies.append(proxy)
                    results.add_row([proxy, "Unknown", "Not Working"])
            except:
                non_working_proxies.append(proxy)
                results.add_row([proxy, "Unknown", "Not Working"])

    print(results)
    print(f"\nWorking proxies: {len(working_proxies)}")
    print(f"Non-working proxies: {len(non_working_proxies)}")


