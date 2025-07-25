#!/usr/bin/env python3

import os
import sys
import json
import requests
import random
import string
import time
from pathlib import Path

def generate_nonce(length=16):
    """生成指定长度的随机字符串"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_expires_at():
    """生成过期时间戳（当前时间 + 1分钟）"""
    return int(time.time()) + 60

def read_env_json():
    """读取env.json文件"""
    env_file = Path("env.json")
    if not env_file.exists():
        print("错误: env.json 文件不存在，请先运行 build2.py")
        sys.exit(1)
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取env.json失败: {e}")
        sys.exit(1)

def read_deploy_log():
    """读取当前目录下的deploy.log文件"""
    log_file = Path("deploy.log")
    if not log_file.exists():
        print("错误: deploy.log 文件不存在")
        sys.exit(1)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取deploy.log失败: {e}")
        sys.exit(1)

def upload_report(job_id, api_origin, is_success, run_log):
    """上传报告到API"""
    url = f"{api_origin}/api/cicd/deploy/report"
    headers = {
        "Content-Type": "application/json"
    }
    
    # 生成nonce和expires_at
    nonce = generate_nonce(16)
    expires_at = generate_expires_at()
    
    data = {
        "nonce": nonce,
        "expires_at": expires_at,
        "job_id": job_id,
        "run_log": run_log,
        "is_success": is_success
    }
    
    print(f"上传报告参数:")
    print(f"  nonce: {nonce}")
    print(f"  expires_at: {expires_at}")
    print(f"  job_id: {job_id}")
    print(f"  is_success: {is_success}")
    print(f"  run_log长度: {len(run_log)} 字符")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") == "ok":
            print("报告上传成功")
        else:
            print(f"API返回错误: {result}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"上传报告失败: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("用法: python3 report.py <api_origin> <is_success>")
        print("示例: python3 report.py https://app-dev.dayu.me true")
        print("参数说明:")
        print("  api_origin: API服务器地址")
        print("  is_success: 是否成功 (true/false)")
        sys.exit(1)
    
    api_origin = sys.argv[1]
    is_success_str = sys.argv[2].lower()
    
    # 验证is_success参数
    if is_success_str not in ['true', 'false']:
        print("错误: is_success 参数必须是 'true' 或 'false'")
        sys.exit(1)
    
    is_success = is_success_str == 'true'
    
    print(f"开始上传报告...")
    print(f"  api_origin: {api_origin}")
    print(f"  is_success: {is_success}")
    
    # 读取env.json获取job_id
    print("正在读取env.json...")
    env_data = read_env_json()
    
    if env_data.get("code") != "ok":
        print(f"env.json中的API响应错误: {env_data}")
        sys.exit(1)
    
    body = env_data.get("body", {})
    job_id = body.get("job_id")
    
    if not job_id:
        print("错误: env.json中未找到job_id")
        sys.exit(1)
    
    print(f"从env.json获取到job_id: {job_id}")
    
    # 读取deploy.log
    print("正在读取deploy.log...")
    run_log = read_deploy_log()
    
    # 上传报告
    print("正在上传报告到API...")
    upload_report(job_id, api_origin, is_success, run_log)
    
    print("报告上传完成")

if __name__ == "__main__":
    main()
