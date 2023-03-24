import threading
import queue
import time
import sys
import requests
from bs4 import BeautifulSoup
from pyfiglet import Figlet
from termcolor import colored
import socket
from tqdm import tqdm
import argparse
from proxy_location import test_and_locate_proxies_in_file
from proxy_test import load_proxies_from_file
from proxy_test import test_proxiess
from p_utils import detect_chaining



def get_proxies_worker(proxy_type, location, num_proxies, proxy_queue):
    if not proxy_type and not location:
        # If proxy_type and location are empty, scrape all available proxies from each URL
        url_list = [
            'https://www.sslproxies.org/',
            'https://free-proxy-list.net/',
            'https://www.us-proxy.org/',
            'https://www.socks-proxy.net/',
            'https://www.proxy-list.download/api/v1/get?type=https&page=1&anon=elite',
            'https://www.proxy-list.download/api/v1/get?type=socks4&page=1&anon=elite',
            'https://www.proxy-list.download/api/v1/get?type=socks5&page=1&anon=elite',
            'https://www.proxyscan.io/download?type=http&ping=500'
        ]
    else:
        # Otherwise, scrape proxies that match the specified type and location
        url_list = [
            f'https://www.sslproxies.org/{location}-proxy-list.html',
            f'https://free-proxy-list.net/{location}-proxy.html',
            f'https://www.us-proxy.org/{location}-proxy/{num_proxies}',
            f'https://www.socks-proxy.net/{location.lower()}.html',
        ]

        if proxy_type == 'https':
            url_list.append(f'https://www.proxy-list.download/api/v1/get?type=https&page=1&anon=elite')
        elif proxy_type == 'socks4':
            url_list.append(f'https://www.proxy-list.download/api/v1/get?type=socks4&page=1&anon=elite')
        elif proxy_type == 'socks5':
            url_list.append(f'https://www.proxy-list.download/api/v1/get?type=socks5&page=1&anon=elite')

    for url in url_list:
        try:
            page = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            continue

        soup = BeautifulSoup(page.content, 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if cols:
                proxy = cols[0].text + ':' + cols[1].text
                proxy_queue.put(proxy)

def generate_proxies():
    proxy_queue = queue.Queue()
    num_proxies = int(input('Enter the number of proxies to generate: '))
    proxy_type = input('Enter the type of proxy (http/https/socks4/socks5): ')
    location = input('Enter the location of the proxy (US/CA/GB/FR/DE/etc.): ')

    print(f'Finding {num_proxies} {proxy_type} proxies from {location}...')

    threads = []
    for i in range(10):
        t = threading.Thread(target=get_proxies_worker, args=(proxy_type, location, num_proxies//10, proxy_queue))
        threads.append(t)
        t.start()

    proxies = []
    while len(proxies) < num_proxies:
        try:
            proxy = proxy_queue.get(timeout=1)
            proxies.append(proxy)
        except queue.Empty:
            continue

    print(f'{len(proxies)} {proxy_type} proxies found from {location}!')
    return proxies

def generate_proxies_multithread(num_proxies, proxy_type="", location=""):
    if not proxy_type and not location:
        print("Both 'proxy_type' and 'location' parameters are empty, showing available proxies...")
        
    proxy_list = []
    page_num = 1
    proxy_count = 0
    
    print(f"Finding {num_proxies} {location} {proxy_type} proxies using multithreading...")
    
    def scrape_proxy_urls(url_list):
        nonlocal proxy_list, proxy_count
        for url in url_list:
            try:
                page = requests.get(url)
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                continue
            soup = BeautifulSoup(page.content, "html.parser")
            rows = soup.find_all("tr")
            
            for row in rows:
                cols = row.find_all("td")
                if cols:
                    if proxy_type and location:
                        if cols[4].text == proxy_type and cols[3].text == location:
                            proxy = {
                                "type": cols[4].text,
                                "location": cols[3].text,
                                "ip_address": cols[0].text,
                                "port": cols[1].text
                            }
                            proxy_list.append(proxy)
                            proxy_count += 1
                            if proxy_count >= num_proxies:
                                break
                    else:
                        proxy = {
                            "type": cols[4].text,
                            "location": cols[3].text,
                            "ip_address": cols[0].text,
                            "port": cols[1].text
                        }
                        proxy_list.append(proxy)
                        proxy_count += 1
                        if proxy_count >= num_proxies:
                            break
            
            if proxy_count >= num_proxies:
                break
    
    url_lists = [
        [
            f"https://www.us-proxy.org/page/{page_num}",
            f"https://free-proxy-list.net/anonymous-proxy.html#{page_num}",
            f"https://www.sslproxies.org/page/{page_num}/"
        ],
        [
            f"https://www.socks-proxy.net/?page={page_num}",
            f"https://www.proxy-list.download/api/v1/get?type=http&page={page_num}&anon=elite",
            f"https://www.proxyscan.io/download?type=http&page={page_num}&ping=500"
        ]
    ]
    
    threads = []
    
    for url_list in url_lists:
        thread = threading.Thread(target=scrape_proxy_urls, args=(url_list,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(f"{len(proxy_list)} {location} {proxy_type} proxies found using multithreading!")
    return proxy_list


def display_banner():
    custom_fig = Figlet(font='graffiti')
    print(colored(custom_fig.renderText('Proxies Cat'), 'red', attrs=['bold']))
    print(colored('Author: Tejas (Linterex Community)').rjust(70))

def display_proxies(proxy_list):
    display_banner()
    print('\n')
    print("Type\tLocation\tIP Address\tPort")
    for i, proxy in enumerate(proxy_list):
        proxy_type = proxy['type']
        location = proxy['location']
        ip_address = proxy['ip_address']
        port = proxy['port']
        print(f"{proxy_type}\t{location}\t{ip_address}\t{port}")
    print('\n')
    print('Author: Tejas'.center(50, ' '))

def save_to_file(proxy_list):
    filename = input("Enter the filename to save the proxies: ")
    with open(filename, 'w') as f:
        for proxy in proxy_list:
            f.write(f"{proxy['ip_address']}:{proxy['port']}\n")
    print(f"Proxies saved to {filename} file!")

def test_proxies(proxies):
    working_proxies = []
    non_working_proxies = []
    timeout = 2 # set timeout to 2 seconds
    for proxy in tqdm(proxies, desc="Testing proxies", leave=False):
        ip = proxy['ip_address']
        port = proxy['port']
        protocol = ''
        try:
            # HTTP test
            response = requests.get('http://www.example.com', proxies={'http': f'http://{ip}:{port}'}, timeout=timeout)
            protocol = 'HTTP'
        except:
            pass
        if not protocol:
            try:
                # HTTPS test
                response = requests.get('https://www.example.com', proxies={'https': f'https://{ip}:{port}'}, timeout=timeout)
                protocol = 'HTTPS'
            except:
                pass
        if not protocol:
            try:
                # SOCKS4 test
                socks_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socks_socket.settimeout(timeout)
                socks_socket.connect((ip, int(port)))
                socks_socket.send(b'\x04\x01\x00\x50\x11\x22\x33\x44\x55')
                response = socks_socket.recv(8)
                if response[1] == b'\x5a':
                    protocol = 'SOCKS4'
            except:
                pass
        if not protocol:
            try:
                # SOCKS5 test
                socks_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socks_socket.settimeout(timeout)
                socks_socket.connect((ip, int(port)))
                socks_socket.send(b'\x05\x01\x00')
                response = socks_socket.recv(2)
                if response == b'\x05\x00':
                    protocol = 'SOCKS5'
            except:
                pass
        if protocol:
            print(f'{ip}:{port} ({protocol}) - working')
            working_proxies.append({'ip': ip, 'port': port, 'protocol': protocol})
        else:
            print(f'{ip}:{port} ({protocol}) - not working')
            non_working_proxies.append({'ip': ip, 'port': port})
    save_proxies = input('Do you want to save tested working proxies in a file? (Y/N): ')
    if save_proxies.lower() == 'y':
        filename = input('Enter filename to save the proxies: ')
        with open(filename, 'w') as file:
            for proxy in working_proxies:
                file.write(f'{proxy["ip"]}:{proxy["port"]} ({proxy["protocol"]})\n')
        print(f'{len(working_proxies)} proxies saved to {filename}')
    else:
        print(f'{len(working_proxies)} proxies found working')
    print(f'{len(non_working_proxies)} proxies not working')


def test_proxies_in_file(file_path):
    with open(file_path, 'r') as f:
        proxies = [line.strip() for line in f.readlines()]

    results = []
    for i, proxy in enumerate(proxies):
        url = 'https://www.google.com'
        protocol = None
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

        results.append((proxy, protocol))

        # Add a loading animation
        sys.stdout.write('\r')
        sys.stdout.write(f'Identifying Protocol: [{i+1}/{len(proxies)}] {"."*(i%4)}')
        sys.stdout.flush()
        time.sleep(0.2)

    sys.stdout.write('\n')
    return results

#start


def testy_proxy(ip, port, protocol):
    try:
        proxies = {protocol: f'{protocol}://{ip}:{port}'}
        response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def mains():
    parser = argparse.ArgumentParser(description='Test a proxy for connectivity.')
    parser.add_argument('-t', '--test', action='store_true', help='Test the proxy for connectivity')
    parser.add_argument('-i', '--ip', help='The IP address of the proxy')
    parser.add_argument('-p', '--port', help='The port number of the proxy')
    parser.add_argument('-po', '--protocol', choices=['http', 'https', 'socks4', 'socks5'], help='The protocol type of the proxy')

    args = parser.parse_args()

    if args.test:
        if testy_proxy(args.ip, args.port, args.protocol):
            print('Proxy is working.')
        else:
            print('Proxy is not working.')
    else:
      parser.print_help()
    while True:
       response = input('Do you want to continue? (y/n): ')
       if response.lower() == 'y':
           # Continue with the program
           break
       elif response.lower() == 'n':
           # Exit the program
           print('Exiting...')
           exit()
       else:
           print('Invalid input. Please enter y or n.')

def detect_chaining_of_proxies():
    option = input("[1] check a single IP?\n[2] check IPs by file?\n: ")
    if option == '1':
        ip = input("Enter the IP address: ")
        detect_chaining(ip.strip())
    elif option == '2':
        filepath = input("Enter the path of the file containing IPs: ")
        with open(filepath, 'r') as f:
            ips = f.readlines()
        for ip in ips:
            detect_chaining(ip.strip())

if __name__ == '__main__':
    mains()
    print('\n')
    display_banner()
    print('\n')
    
    while True:
        print("\n[1] Generate Proxies\n[2] Test existing proxies by file\n[3] Find proxies protocol type by file\n[4] Find proxies location by file\n[5] Detect Proxies Chaining\n[6] Exit\n")
        try:
            option = input('Enter the option number: ')
            if option == '1':
                num_proxies = int(input('Enter the number of proxies to generate: '))
                proxy_type = input('Enter the type of proxy to generate (http, https, socks4, socks5): ')
                location = input('Enter the location of the proxy to generate (e.g. US, CA, JP, DE): ')
                if not proxy_type.strip() or not location.strip():
                    proxy_type = ''
                    location = ''
                proxies = generate_proxies_multithread(num_proxies, proxy_type, location)
                display_proxies(proxies)
                
                while True:
                    option = input('\nWhat would you like to do?\n[1] Test generated proxies\n[2] Generate more proxies\n[3] Save proxies to a file\n[4] Back to main menu\n\nEnter the option number: ')
                    if option == '1':
                        test_proxies(proxies)
                    elif option == '2':
                        break
                    elif option == '3':
                        save = input('Do you want to save the proxies to a file? (y/n): ')
                        if save.lower() == 'y':
                            save_to_file(proxies)
                        break
                    elif option == '4':
                        break
                    else:
                        print('Invalid option! Please enter a valid option number.')
                        continue
                
                if option == '2':
                    continue
                elif option == '4':
                        continue
                else:
                    break
                
            elif option == '2':
                file_path = input('Enter the path of the file containing the proxies: ')
                proxies = load_proxies_from_file(file_path)
                test_proxiess(proxies)
                
            elif option == '3':
                file_path = input('Enter the path of the file containing the proxies: ')
                results = test_proxies_in_file(file_path)
                for result in results:
                    print(f'\n{result[0]} has {result[1]} protocol.')
            
            elif option == '4':
                file_path = input('Enter the path of the file containing the proxies: ')
                results = test_and_locate_proxies_in_file(file_path)
                print = (results)

            elif option == '5':
                detect_chaining_of_proxies()
            elif option == '6':
                break   
            else:
                print('Invalid option! Please enter a valid option number.')
                continue
                
        except ValueError:
            print('Invalid input! Please enter a valid number for the number of proxies.')
            continue
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            continue
        except Exception as e:
            print(f'Error: {e}')
            continue
