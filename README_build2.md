# build2.py 使用说明

## 概述
`build2.py` 是 `build.sh` 的 Python3 版本，主要功能分为两部分：
1. 从 HTTP 接口获取环境信息，下载并解压 zip 包
2. 执行 everkm-publish 编译页面

## 安装依赖
```bash
pip3 install -r requirements.txt
```

## 使用方法
```bash
python3 build2.py <nonce> <expires_at> <job_id>
```

### 参数说明
- `nonce`: 随机字符串，用于API认证
- `expires_at`: 过期时间戳
- `job_id`: 任务ID

### 示例
```bash
python3 build2.py abc123def456ghi789 1735689600 5TrIp3tDyi
```

## API 接口
脚本会向以下接口发送 POST 请求获取环境信息：
```
POST https://app-dev.dayu.me/api/cicd/deploy/env
```

### 请求体
```json
{
  "nonce": "abc123def456ghi789",
  "expires_at": 1735689600,
  "id": "5TrIp3tDyi"
}
```

### 响应结构
```json
{
    "code": "ok",
    "body": {
        "job_id": "5TrIp3tDyi",
        "member_name": "jcoldyu",
        "youlog": "asdf",
        "version": "v3",
        "git_repo": "",
        "uploaded_content": null,
        "sub_dir": ""
    }
}
```

## 下载逻辑
1. 如果 `body.uploaded_content` 不为空，直接使用该URL下载zip包
2. 如果 `body.uploaded_content` 为空，使用 `body.git_repo` 和 `body.version` 生成GitHub release下载URL

## 输出
脚本会在 `tmp/dist-pages/` 目录下生成编译后的HTML文件，并在最后显示生成的HTML文件数量。

## 注意事项
- 确保 `tmp` 目录存在（可通过运行 `setup_env.sh` 创建）
- 确保已安装 `everkm-publish` 工具
- 需要网络连接来访问API和下载zip包 