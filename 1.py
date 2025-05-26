# -*- coding: UTF-8 -*-
import requests as req
import json, sys, time
import os  # 新增：导入 os 读取环境变量

# 先注册azure应用,确保应用有以下权限:
# files: Files.Read.All、Files.ReadWrite.All、Sites.Read.All、Sites.ReadWrite.All
# user: User.Read.All、User.ReadWrite.All、Directory.Read.All、Directory.ReadWrite.All
# mail: Mail.Read、Mail.ReadWrite、MailboxSettings.Read、MailboxSettings.ReadWrite
# 注册后一定要再点代表xxx授予管理员同意,否则outlook api无法调用

path = sys.path[0] + r'/1.txt'
num1 = 0

# 从环境变量读取client_id和secret
id = os.environ.get("CONFIG_ID")
secret = os.environ.get("CONFIG_KEY")

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
    try:
        with open(path, "r+") as fo:
            refresh_token = fo.read()
    except Exception as e:
        print(f"读取refresh_token失败: {e}")
        return

    localtime = time.asctime(time.localtime(time.time()))
    access_token = gettoken(refresh_token)
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }

    try:
        endpoints = [
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
            'https://graph.microsoft.com/v1.0/me/outlook/masterCategories',
        ]

        for idx, url in enumerate(endpoints, 1):
            resp = req.get(url, headers=headers)
            if resp.status_code == 200:
                num1 += 1
                print(f'{idx}调用成功{num1}次')

        print('此次运行结束时间为 :', localtime)
    except Exception as e:
        print(f"请求异常，跳过: {e}")
        pass

for _ in range(3):
    main()
