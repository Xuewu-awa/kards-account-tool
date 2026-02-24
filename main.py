import requests
import json
import time
import random
import string
import os
from datetime import datetime

# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_VERSION = "++UE5+Release-5.6-CL-44394996"
default_headers = {
    'Host': 'kards.live.1939api.com',
    'Accept-Encoding': 'deflate, gzip',
    'Accept': 'application/json',
    'X-Api-Key': f'1939-kards-5dcda429f:Kards {DEFAULT_VERSION}',
    'Drift-Api-Key': f'1939-kards-5dcda429f:Kards {DEFAULT_VERSION}',
    'Content-Type': 'application/json',
    'User-Agent': 'kards/++UE5+Release-5.6-CL-44394996 (http-eventloop) Windows/10.0.22000.1.256.64bit'
}

REDEEM_CODES = [
    "DOUYIN-9C2E-4E6A-SSR",
    "KARDS-203C-40D9-SSR", 
    "KARDS-665A-444D-SSR",
    "KARDSMADAOCHENGGONG",
    "KARDSRENXINBUZU", 
    "KARDSQIBAOMA",
    "THREADS-EE3D-4B63-SSR"
]

def generate_random_hash():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(32))

def send_redeem_codes(jwt_token):
    headers = dict(default_headers)
    headers['Authorization'] = f'JWT {jwt_token}'
    for code in REDEEM_CODES:
        try:
            requests.get(f"https://kards.live.1939api.com/redeem/{code}?new", 
                        headers=headers, timeout=5, verify=False)
        except:
            pass

def create_account(player_name=None):
    try:
        deviceid = int(time.time() * 1000)
        devicepassword = str(int(time.time() * 1000))
        random_hash = generate_random_hash()
        
        platform_info = {
            "device_profile": "Windows",
            "cpu_vendor": "AuthenticAMD",
            "cpu_brand": "AMD Ryzen Threadripper PRO 9995WX @ 2.50GHz",
            "gpu_brand": "NVIDIA RTX Pro 6000 96GB",
            "num_cores_physical": 10,
            "num_cores_logical": 20,
            "physical_memory_gb": 16,
            "hash": random_hash,
            "locale": "zh-CN"
        }
        
        login_data = {
            "provider": "device_id",
            "provider_details": {"payment_provider": "XSOLLA"},
            "client_type": "UE5",
            "build": f"Kards {DEFAULT_VERSION}",
            "platform_type": "Windows",
            "app_guid": "Kards",
            "version": f"Kards {DEFAULT_VERSION}",
            "platform_info": json.dumps(platform_info),
            "platform_version": "Windows 11 (21H2) [10.0.22000.2538] ",
            "language": "zh-Hans",
            "automatic_account_creation": True,
            "username": f"device:Windows-{deviceid}",
            "password": devicepassword
        }
        
        time.sleep(random.uniform(0.1, 0.3))
        resp = requests.post('https://kards.live.1939api.com/session', 
                           headers=default_headers, json=login_data, verify=False)
        
        if not resp.ok:
            return {'success': False, 'error': f'创建失败: {resp.status_code}'}
        
        data = resp.json()
        jwt = data.get('jwt')
        pid = data.get('player_id')
        
        if not jwt or not pid:
            return {'success': False, 'error': '未获取到JWT'}
        
        # 名称
        auth_headers = dict(default_headers)
        auth_headers['Authorization'] = f'JWT {jwt}'
        
        if not player_name:
            player_name = f"{random.randint(0, 99):02d}号亚硝酸钠"
        
        requests.put(f'https://kards.live.1939api.com/players/{pid}', 
                    headers=auth_headers, 
                    json={"action": "set-name", "value": player_name},
                    verify=False)
        
        # 跳过教程
        tutorials = ["Germany", "Soviet", "Japan", "USA", "Britain"]
        for tutorial in tutorials:
            time.sleep(0.1)
            requests.put(f'https://kards.live.1939api.com/players/{pid}', 
                        headers=auth_headers, 
                        json={"action": "skip-tutorial", "value": tutorial},
                        verify=False)
        
        # 兑换码
        time.sleep(2)
        send_redeem_codes(jwt)
        
        account_info = {
            'username': f"device:Windows-{deviceid}",
            'password': devicepassword,
            'jwt': jwt,
            'pid': pid,
            'display_name': player_name
        }
        
        return {'success': True, 'account': account_info}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def bind_email(jwt, email, email_pwd):
    headers = dict(default_headers)
    headers['Authorization'] = f'JWT {jwt}'
    
    data = {
        "action": "create_new_link",
        "linker_username": email,
        "linker_password": email_pwd
    }
    
    try:
        resp = requests.put('https://kards.live.1939api.com/session',
                          headers=headers, json=data, verify=False)
        
        if resp.status_code == 200:
            return {'success': True}
        else:
            error_msg = f'绑定失败: {resp.status_code}'
            try:
                err = resp.json().get('error')
                if err:
                    error_msg += f' - {err}'
            except:
                pass
            return {'success': False, 'error': error_msg}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def save_to_file(accounts, filename="accounts.txt"):
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            for acc in accounts:
                f.write(f"{acc['email']}|{acc['email_pwd']}|{acc['device_username']}|{acc['device_pwd']}|{acc['display_name']}\n")
        return True
    except:
        return False

def main():
    print("Kards 账号建号脚本 by 氧化铜")
    print("——" * 20)
    
    accounts_to_save = []
    
    while True:
        #  创建
        print("\n1. 创建新账号")
        name = input("输入玩家名称 (直接回车使用默认名称): ").strip()
        if not name:
            name = None
        
        print("正在创建账号...")
        result = create_account(name)
        
        if not result['success']:
            print(f"创建失败: {result['error']}")
            continue
        
        acc = result['account']
        print(f"账号创建成功: {acc['display_name']}")
        print(f"用户名: {acc['username']}")
        print(f"密码: {acc['password']}")
        
        #  绑邮箱
        print("\n2. 绑定邮箱")
        email = input("输入邮箱地址: ").strip()
        if not email:
            print("邮箱不能为空")
            continue
        
        email_pwd = input("输入邮箱密码: ").strip()
        if not email_pwd:
            print("密码不能为空")
            continue
        
        print("正在绑定邮箱...")
        bind_result = bind_email(acc['jwt'], email, email_pwd)
        
        if bind_result['success']:
            print("邮箱绑定成功")
            
            # 保存到列表
            accounts_to_save.append({
                'email': email,
                'email_pwd': email_pwd,
                'device_username': acc['username'],
                'device_pwd': acc['password'],
                'display_name': acc['display_name']
            })
            
            # 保存到文件
            save_to_file([accounts_to_save[-1]])
            print("账号信息已保存到 accounts.txt")
        else:
            print(f"绑定失败: {bind_result['error']}")
          
            ans = input("是否保存设备账号信息到文件？(y/n): ").strip().lower()
            if ans == 'y':
                with open("device_accounts.txt", 'a', encoding='utf-8') as f:
                    f.write(f"{acc['username']}|{acc['password']}|{acc['display_name']}\n")
                print("设备账号信息已保存到 device_accounts.txt")
        
        
        print("\n" + "——" * 20)
        again = input("是否继续创建下一个账号？(y/n): ").strip().lower()
        if again != 'y':
            break
    
    # 显示统计
    if accounts_to_save:
        print(f"\n本次共创建并绑定了 {len(accounts_to_save)} 个账号")
        print("所有账号信息已保存在 accounts.txt")
    
    print("程序结束")

if __name__ == "__main__":
    main()