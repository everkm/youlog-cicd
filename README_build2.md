# build2.py 使用说明

## 概述
`build2.py` 是一个完整的 CI/CD 构建脚本，集成了以下功能：
1. 从 HTTP 接口获取环境信息，下载并解压 zip 包
2. 执行 everkm-publish 编译页面
3. 上传 CDN 资源
4. 压缩 HTML 文件为 .gz 格式
5. 创建 ZIP 包

## 安装依赖
```bash
pip3 install -r requirements.txt
```

## 使用方法
```bash
python3 build2.py <job_id> <api_origin>
```

### 参数说明
- `job_id`: 任务ID
- `api_origin`: API 服务器地址（包含协议和域名）

### 示例
```bash
python3 build2.py 5TrIp3tDyi https://app-dev.dayu.me
```

## 自动生成的参数
脚本会自动生成以下参数：
- `nonce`: 16位随机字符串（字母+数字）
- `expires_at`: 当前时间戳 + 60秒

## API 接口
脚本会向以下接口发送 POST 请求获取环境信息：
```
POST {api_origin}/api/cicd/deploy/env
```

### 请求体
```json
{
  "nonce": "aB3cD4eF5gH6iJ7k",
  "expires_at": 1735689660,
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

## 构建流程

### 第一部分：获取环境信息并下载代码
1. 生成 `nonce` 和 `expires_at` 参数
2. 从 API 获取环境信息
3. 根据 `uploaded_content` 或 `git_repo` + `version` 确定下载URL
4. 下载并解压 zip 文件

### 第二部分：编译页面
1. 执行 `everkm-publish` 命令编译页面
2. 统计生成的 HTML 文件数量

### 第三部分：后处理
1. **CDN 上传**：
   - 检查七牛云密钥环境变量（`QINIU_ACCESS_KEY`, `QINIU_SECRET_KEY`）
   - 上传 assets 目录到 CDN
   
2. **HTML 文件压缩**：
   - 将所有 `.html` 文件压缩为 `.html.gz`
   - 删除原始 `.html` 文件
   
3. **ZIP 包创建**：
   - 创建 `{youlog}@{version}.zip` 文件
   - 使用 Stored 模式（不压缩）
   - 保持目录结构

## 下载逻辑
1. 如果 `body.uploaded_content` 不为空，直接使用该URL下载zip包
2. 如果 `body.uploaded_content` 为空，使用 `body.git_repo` 和 `body.version` 生成GitHub release下载URL

## 输出文件
- **编译后的页面**: `tmp/dist-pages/` 目录
- **ZIP 包**: `{youlog}@{version}.zip` 文件
- **压缩的 HTML**: `.html.gz` 文件

## 环境变量
- `QINIU_ACCESS_KEY`: 七牛云 Access Key（可选）
- `QINIU_SECRET_KEY`: 七牛云 Secret Key（可选）
- `EVERKM_LOG`: 设置为 "error" 减少日志输出

## 注意事项
- 确保 `tmp` 目录存在（可通过运行 `setup_env.sh` 创建）
- 确保已安装 `everkm-publish` 工具
- 确保已安装 `qshell` 工具（用于 CDN 上传）
- 需要网络连接来访问 API 和下载 zip 包
- 如果未设置七牛云密钥，CDN 上传步骤会被跳过

## 统计信息
脚本运行完成后会显示：
- 生成的 HTML 文件数量
- 压缩后的 `.html.gz` 文件数量
- ZIP 文件大小
- ZIP 文件位置 