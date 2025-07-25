#!/usr/bin/env python3

import os
import sys
import json
import requests
import zipfile
import shutil
import subprocess
from pathlib import Path
import tempfile
import urllib.parse
import gzip
import random
import string
import time

def generate_nonce(length=16):
    """生成指定长度的随机字符串"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_expires_at():
    """生成过期时间戳（当前时间 + 1分钟）"""
    return int(time.time()) + 60

def get_env_info(nonce, expires_at, job_id, api_origin):
    """从HTTP接口获取环境信息"""
    url = f"{api_origin}/api/cicd/deploy/env"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "nonce": nonce,
        "expires_at": expires_at,
        "id": job_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        sys.exit(1)



def download_and_extract_zip(zip_url, extract_dir):
    """下载并解压zip文件"""
    try:
        print(f"正在下载zip文件: {zip_url}")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()
        
        # 创建临时文件保存zip
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # 解压文件
        print(f"正在解压到: {extract_dir}")
        with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        print("下载和解压完成")
        
    except Exception as e:
        print(f"下载或解压失败: {e}")
        sys.exit(1)

def generate_release_url(git_repo, version):
    """根据git_repo和version生成release下载URL"""
    # git_repo格式为 {owner}/{repo}
    if "/" in git_repo:
        owner, repo = git_repo.split("/", 1)
        # 生成GitHub release下载URL
        return f"https://github.com/{owner}/{repo}/archive/refs/tags/{version}.zip"
    else:
        print(f"不支持的git仓库格式: {git_repo}，期望格式为 owner/repo")
        sys.exit(1)

def run_everkm_publish(work_dir, base_prefix, cdn_prefix, theme_dir, dist_dir):
    """执行everkm-publish命令"""
    cmd = [
        "./tmp/everkm-publish", "serve",
        "--work-dir", work_dir,
        "--base-prefix", base_prefix,
        "--cdn-prefix", cdn_prefix,
        "--theme-dir", theme_dir,
        "--dist-dir", dist_dir,
        "--export"
    ]
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env["EVERKM_LOG"] = "error"
        
        print("正在执行 everkm-publish...")
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print("everkm-publish 执行成功")
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"everkm-publish 执行失败: {e}")
        print(f"标准输出(stdout): {e.stdout}")
        print(f"错误输出(stderr): {e.stderr}")
        sys.exit(1)

def count_html_files(dist_dir):
    """统计HTML文件数量"""
    html_files = list(Path(dist_dir).rglob("*.html"))
    return len(html_files)

def upload_to_cdn(target_dir, member_name, youlog):
    """上传CDN资源"""
    qiniu_access_key = os.environ.get('QINIU_ACCESS_KEY')
    qiniu_secret_key = os.environ.get('QINIU_SECRET_KEY')
    
    if not qiniu_access_key or not qiniu_secret_key:
        print("警告: QINIU_ACCESS_KEY 或 QINIU_SECRET_KEY 未设置，跳过CDN上传")
        return
    
    # 设置 qshell 账户
    try:
        subprocess.run([
            "./qshell", "account", qiniu_access_key, qiniu_secret_key, "everkm", "-w"
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"设置 qshell 账户失败: {e}")
        return
    
    # 统计文件数量
    assets_dir = Path(target_dir) / "assets"
    if assets_dir.exists():
        file_count = len(list(assets_dir.rglob("*")))
        print(f"上传CDN: {file_count} 个文件")
        
        # 执行上传
        try:
            subprocess.run([
                "./qshell", "qupload2",
                "--silence",
                "--src-dir", str(assets_dir),
                "--key-prefix", f"yl-member/{member_name}/{youlog}/assets/",
                "--bucket", "dayu-assets",
                "--thread-count", "5",
                "--overwrite",
                "--check-hash",
                "--rescan-local=true",
                "--skip-fixed-strings", ".DS_Store"
            ], check=True)
            print("CDN上传完成")
        except subprocess.CalledProcessError as e:
            print(f"CDN上传失败: {e}")
    else:
        print("assets目录不存在，跳过CDN上传")

def compress_html_files(target_dir):
    """压缩HTML文件为.gz格式"""
    target_path = Path(target_dir)
    html_files = list(target_path.rglob("*.html"))
    
    print(f"开始压缩 {len(html_files)} 个HTML文件...")
    
    for html_file in html_files:
        try:
            # 读取HTML文件内容
            with open(html_file, 'rb') as f:
                content = f.read()
            
            # 压缩为gz格式
            with gzip.open(f"{html_file}.gz", 'wb') as f:
                f.write(content)
            
            # 删除原HTML文件
            html_file.unlink()
            
        except Exception as e:
            print(f"压缩文件 {html_file} 失败: {e}")
    
    print("HTML文件压缩完成")

def create_zip_package(target_dir, member_name, youlog, version, current_dir):
    """创建ZIP包"""
    zip_name = f"{youlog}@{version}.zip"
    version_dir = f"{member_name}/{youlog}/v{version}"
    
    # 删除已存在的zip文件
    zip_path = Path(current_dir) / zip_name
    if zip_path.exists():
        zip_path.unlink()
    
    # 创建ZIP文件
    target_path = Path(target_dir) / version_dir
    if not target_path.exists():
        print(f"错误: 目录 '{target_path}' 不存在")
        return None
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as zipf:
            for file_path in target_path.rglob("*"):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(target_path)
                    zipf.write(file_path, arcname)
        
        print(f"打包完成: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"创建ZIP文件失败: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print("用法: python3 build2.py <job_id> <api_origin>")
        print("示例: python3 build2.py 5TrIp3tDyi https://app-dev.dayu.me")
        sys.exit(1)
    
    job_id = sys.argv[1]
    api_origin = sys.argv[2]
    
    # 内部生成 nonce 和 expires_at
    nonce = generate_nonce(16)
    expires_at = generate_expires_at()
    
    print(f"生成的参数:")
    print(f"  nonce: {nonce}")
    print(f"  expires_at: {expires_at}")
    print(f"  job_id: {job_id}")
    print(f"  api_origin: {api_origin}")
    
    current_dir = Path.cwd()
    build_dir = current_dir / "tmp"
    
    if not build_dir.exists():
        print("BUILD_DIR 不存在，请先运行 setup_env.sh")
        sys.exit(1)
    
    # 第一部分：从HTTP接口获取环境信息并下载zip包
    print("=== 第一部分：获取环境信息并下载代码 ===")
    
    # 获取环境信息
    print("正在从API获取环境信息...")
    response_data = get_env_info(nonce, expires_at, job_id, api_origin)
    
    if response_data.get("code") != "ok":
        print(f"API返回错误: {response_data}")
        sys.exit(1)
        
    # 写入环境信息到文件
    with open("env.json", "w") as f:
        json.dump(response_data, f, indent=4)
    
    body = response_data.get("body", {})
    member_name = body.get("member_name")
    youlog = body.get("youlog")
    version = body.get("version")
    version_prefix = body.get("version_prefix")
    git_repo = body.get("git_repo")
    uploaded_content = body.get("uploaded_content")
    sub_dir = body.get("sub_dir")
    
    print(f"获取到环境信息:")
    print(f"  member_name: {member_name}")
    print(f"  youlog: {youlog}")
    print(f"  version: {version}")
    print(f"  version_prefix: {version_prefix}")
    print(f"  git_repo: {git_repo}")
    print(f"  uploaded_content: {uploaded_content}")
    print(f"  sub_dir: {sub_dir}")
    
    # 确定zip下载URL
    if uploaded_content:
        zip_url = uploaded_content
        print(f"使用上传的内容URL: {zip_url}")
    elif git_repo and version:
        zip_url = generate_release_url(git_repo, version)
        print(f"使用生成的release URL: {zip_url}")
    else:
        print("错误: 既没有uploaded_content也没有git_repo和version")
        sys.exit(1)
    
    # 准备下载目录
    src_dir = build_dir / "src"
    if src_dir.exists():
        shutil.rmtree(src_dir)
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # 下载并解压zip文件
    download_and_extract_zip(zip_url, src_dir)

    # 自动检测 src 下的唯一一级目录作为 zip_basename
    entries = [e for e in src_dir.iterdir() if e.is_dir()]
    if len(entries) == 1:
        zip_basename = entries[0].name
    else:
        print(f"src 目录下有多个文件或目录，不确定一级目录名。实际内容: {[e.name for e in src_dir.iterdir()]}")
        sys.exit(1)

    # 第二部分：执行everkm-publish编译页面
    print("\n=== 第二部分：编译页面 ===")
    
    # release_version 是 youlog 的版本号, 不包含tag前缀
    # 从 version 中去掉前缀得到 release_version
    if version.startswith(version_prefix):
        release_version = version[len(version_prefix):]
    else:
        release_version = version

    # 构建参数
    if sub_dir:
        work_dir = str(src_dir / zip_basename / sub_dir)
    else:
        work_dir = str(src_dir / zip_basename)
    base_prefix = f"/{member_name}/{youlog}/v{release_version}/"
    cdn_prefix = f"https://assets.daobox.cc/yl-member/{member_name}/{youlog}/"
    theme_dir = str(build_dir / "youlog")
    dist_dir = str(build_dir / "dist-pages")
    
    print(f"工作目录: {work_dir}")
    print(f"基础前缀: {base_prefix}")
    print(f"CDN前缀: {cdn_prefix}")
    print(f"主题目录: {theme_dir}")
    print(f"输出目录: {dist_dir}")
    
    # 执行everkm-publish
    run_everkm_publish(work_dir, base_prefix, cdn_prefix, theme_dir, dist_dir)
    
    # 统计HTML文件数量
    html_count = count_html_files(dist_dir)
    print(f"\n产出 HTML 文件: {html_count} 个")
    
    # 第三部分：上传CDN、压缩HTML、创建ZIP包
    print("\n=== 第三部分：后处理 ===")
    
    # 上传CDN
    print("开始上传CDN资源...")
    upload_to_cdn(dist_dir, member_name, youlog)
    
    # 压缩HTML文件
    print("开始压缩HTML文件...")
    compress_html_files(dist_dir)
    
    # 创建ZIP包
    print("开始创建ZIP包...")
    zip_path = create_zip_package(dist_dir, member_name, youlog, release_version, current_dir)
    
    # 显示最终统计信息
    if zip_path and zip_path.exists():
        zip_size = zip_path.stat().st_size
        print(f"\n最终统计信息:")
        print(f"ZIP文件: {zip_path}")
        print(f"ZIP文件大小: {zip_size / 1024 / 1024:.2f} MB")
        
        # 统计压缩后的gz文件数量
        gz_count = len(list(Path(dist_dir).rglob("*.html.gz")))
        print(f"压缩后的 .html.gz 文件数量: {gz_count}")

if __name__ == "__main__":
    main()
