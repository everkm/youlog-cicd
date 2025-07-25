# report.py 使用说明

## 功能
report.py 脚本用于将当前目录下的 `deploy.log` 文件通过 API `/api/cicd/deploy/report` 上传到服务器。

## 前置条件
1. 必须先运行 `build2.py` 生成 `env.json` 文件
2. 当前目录下必须存在 `deploy.log` 文件
3. 需要安装 Python 依赖：`pip install -r requirements.txt`

## 使用方法

### 激活虚拟环境（推荐）
```bash
source .py/bin/activate
```

### 运行脚本
```bash
python report.py <api_origin> <is_success>
```

### 参数说明
- `api_origin`: API服务器地址，例如 `https://app-dev.dayu.me`
- `is_success`: 是否成功，必须是 `true` 或 `false`

### 使用示例
```bash
# 成功的情况
python report.py https://app-dev.dayu.me true

# 失败的情况
python report.py https://app-dev.dayu.me false
```

## 工作流程
1. 读取 `env.json` 文件获取 `job_id`
2. 读取 `deploy.log` 文件内容
3. 生成 `nonce` 和 `expires_at` 参数
4. 调用 API `/api/cicd/deploy/report` 上传报告

## API 参数
根据 OpenAPI 文档，上传的参数包括：
- `nonce`: 随机字符串（16位）
- `expires_at`: 过期时间戳（当前时间 + 1分钟）
- `job_id`: 任务ID（从 env.json 读取）
- `run_log`: 运行日志内容（从 deploy.log 读取）
- `is_success`: 是否成功（布尔值）

## 错误处理
- 如果 `env.json` 不存在，会提示先运行 `build2.py`
- 如果 `deploy.log` 不存在，会报错退出
- 如果 API 调用失败，会显示错误信息并退出 