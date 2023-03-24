# Advance Proxy Scraping, Proxy Recon, and Proxy Chaining Detection Tool
This is an advanced tool that allows you to test proxies for connectivity and perform various proxy-related operations. Below are the features of this tool:

![proxycat](https://user-images.githubusercontent.com/94799915/227518792-86279815-f320-4977-8b40-eab42c6d4c98.png)

## Features
### Test Proxy Connectivity
Use the **`-t`** or **`--test`** option to test a proxy for connectivity. You will need to provide the IP address, port number, and protocol type of the proxy using the **`-i`**, **`-p`**, and **`-po`** options respectively. for help you can use **`-h`** and **`--help`**

### Generate Proxies
Use the **`1`** option to generate a list of proxies. The tool allows you to generate any number of proxies and scrape proxies based on the user's input of the desired proxy type and location. After generating the proxies, the tool will ask the user to test the proxies and save the working proxies in a file.

### Test Existing Proxies by File
Use the **`2`** option to test existing proxies stored in a file. The tool will ask the user to provide the file path containing the list of proxies. It will then test the proxies for connectivity and save the working proxies in a separate file.

### Find Proxies Protocol Type by File
Use the **`3`** option to find the protocol type of existing proxies stored in a file. The tool will ask the user to provide the file path containing the list of proxies. It will then analyze the proxies and provide the protocol type of each proxy.

### Find Proxies Location by File
Use the **`4`** option to find the location of existing proxies stored in a file. The tool will ask the user to provide the file path containing the list of proxies. It will then analyze the proxies and provide the location of each proxy.

### Detect Proxies Chaining
Use the **`5`** option to detect if proxies are chained. The tool will ask the user to provide the list of proxies. It will then analyze the proxies and detect if there is a chain between them.

## Installation
To install this tool, follow the steps below:

```
$ git clone https://github.com/proxytool/proxytool.git
$ cd proxies-cat
$ pip install -r requirements.txt
$ python pcat.py
```

## Social Media
Follow us on social media for more updates and information:

* Instagram: @linterex_
* Twitter: @linterex
* Telegram Channel: @linterex

Thank you for using our tool!
