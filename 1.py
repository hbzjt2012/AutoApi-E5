# -*- coding: UTF-8 -*-
import requests as req
import json, sys, time, os

id = os.getenv('CONFIG_ID')
secret = os.getenv('CONFIG_KEY')

if not id or not secret:
    raise ValueError("环境变量 CONFIG_ID 或 CONFIG_KEY 未设置")

path = sys.path[0] + r'/1.txt'
num1 = 0

def gettoken(refresh_token):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': id,
        'client_secret': secret,
        'redirect_uri': 'http://localhost:53682/'
    }
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data, headers=headers)
    jsontxt = json.loads(html.text)
    if 'refresh_token' not in jsontxt:
        print("获取token失败，返回数据如下:")
        print(jsontxt)
        raise ValueError("Token 刷新失败，返回数据中缺少 refresh_token")
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    with open(path, 'w+') as f:
        f.write(refresh_token)
    return access_token

def main():
    global num1
    localtime = time.asctime(time.localtime(time.time()))
    with open(path, "r+") as fo:
        refresh_token = fo.read()
    access_token = gettoken(refresh_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        urls = [
            'https://graph.microsoft.com/v1.0/me/drive/root',
            'https://graph.microsoft.com/v1.0/me/drive',
            'https://graph.microsoft.com/v1.0/drive/root',
            'https://graph.microsoft.com/v1.0/users',
            'https://graph.microsoft.com/v1.0/me/messages',
            'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
            'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages/delta',
            'https://graph.microsoft.com/v1.0/me/drive/root/children',
            'https://api.powerbi.com/v1.0/myorg/apps',
            'https://graph.microsoft.com/v1.0/me/mailFolders',
            'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
        ]
        for i, url in enumerate(urls, start=1):
            resp = req.get(url, headers=headers)
            if resp.status_code == 200:
                num1 += 1
                print(f"{i}调用成功{num1}次")
        print('此次运行结束时间为 :', localtime)
    except Exception as e:
        print("异常：", e)
        pass

for _ in range(3):
    main()
