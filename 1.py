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
    resp = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data, headers=headers)
    try:
        jsontxt = resp.json()
    except json.JSONDecodeError:
        print("响应不是有效的JSON，原始响应内容：", resp.text)
        raise

    if 'refresh_token' not in jsontxt or 'access_token' not in jsontxt:
        print("获取token失败，返回数据如下:")
        print(jsontxt)
        raise ValueError("Token 刷新失败，返回数据中缺少 refresh_token 或 access_token")

    # 保存新的 refresh_token
    new_refresh_token = jsontxt['refresh_token']
    with open(path, 'w+') as f:
        f.write(new_refresh_token)
    return jsontxt['access_token']

def main():
    global num1
    localtime = time.asctime(time.localtime(time.time()))
    try:
        with open(path, "r") as fo:
            refresh_token = fo.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"刷新令牌文件 {path} 不存在，请确保该文件存在且包含有效的refresh_token")

    access_token = gettoken(refresh_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

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
    try:
        for i, url in enumerate(urls, start=1):
            resp = req.get(url, headers=headers)
            if resp.status_code == 200:
                num1 += 1
                print(f"{i} 调用成功 {num1} 次")
            else:
                print(f"{i} 调用失败，状态码：{resp.status_code}，URL：{url}")
        print('此次运行结束时间为 :', localtime)
    except Exception as e:
        print("请求异常：", e)

for _ in range(3):
    main()
