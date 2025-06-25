#!/bin/bash

set -e

# 工具版本号
EVERKM_PUBLISH_VERSION="0.14.1"
THEME_YOULOG_VERSION="0.2.4"
QSHELL_VERSION="2.16.1"

CURRENT_DIR=$(pwd)
BUILD_DIR="$CURRENT_DIR/tmp"

if [ -d "$BUILD_DIR" ]; then
    rm -rf $BUILD_DIR
fi
mkdir -p $BUILD_DIR
cd $BUILD_DIR

# EVERKM-PUBLISH SUFFIX
EKMP_SUFFIX=""
QSHELL_SUFFIX=""

if [ "$(uname)" == "Darwin" ]; then
    EKMP_SUFFIX="darwin-universal"
    QSHELL_SUFFIX="darwin-arm64"
elif [ "$(uname)" == "Linux" ]; then
    EKMP_SUFFIX="linux-amd64"
    QSHELL_SUFFIX="linux-amd64"
else
    echo "不支持的操作系统"
    exit 1
fi


# download qshell
# wget https://github.com/qiniu/qshell/releases/download/v2.16.1/qshell-v2.16.1-linux-arm64.tar.gz
wget --quiet https://github.com/qiniu/qshell/releases/download/v${QSHELL_VERSION}/qshell-v${QSHELL_VERSION}-${QSHELL_SUFFIX}.tar.gz
tar -zxvf qshell-v${QSHELL_VERSION}-${QSHELL_SUFFIX}.tar.gz
# mv qshell-v2.16.1-${QSHELL_SUFFIX}/qshell ./qshell


# 安装 everkm-publish
# https://api.github.com/repos/everkm/publish/releases/latest
# 获取 `"tag_name": "everkm-publish@v0.14.0"` 中, v0.14.0 的值
# 拼接下载地址 https://github.com/everkm/publish/releases/download/everkm-publish%40v0.14.0/EverkmPublish_0.14._${EKMP_SUFFIX}.zip
# 解析压缩包, 获取 EverkmPublish 文件

echo "正在获取 everkm-publish 最新版本信息..."

# 获取最新版本信息
# LATEST_RELEASE=$(curl -s https://api.github.com/repos/everkm/publish/releases/latest)

# 提取 tag_name 中的版本号
# TAG_NAME=$(echo "$LATEST_RELEASE" | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4)
# VERSION=$(echo "$TAG_NAME" | sed 's/everkm-publish@v//')
# echo "Everkm-Publish 最新版本: $VERSION"

# 构建下载地址
DOWNLOAD_URL="https://github.com/everkm/publish/releases/download/everkm-publish%40v${EVERKM_PUBLISH_VERSION}/EverkmPublish_${EVERKM_PUBLISH_VERSION}_${EKMP_SUFFIX}.zip"

echo "下载地址: $DOWNLOAD_URL"

# 下载文件
wget --quiet "$DOWNLOAD_URL" -O "EverkmPublish_${EVERKM_PUBLISH_VERSION}_${EKMP_SUFFIX}.zip"

# 解压文件
unzip "EverkmPublish_${EVERKM_PUBLISH_VERSION}_${EKMP_SUFFIX}.zip"

# 移动 EverkmPublish 文件到当前目录
mv EverkmPublish_${EVERKM_PUBLISH_VERSION}_${EKMP_SUFFIX}/everkm-publish ./everkm-publish

# 设置执行权限
chmod +x ./everkm-publish



# 下载 theme-youlog
# latest: https://api.github.com/repos/everkm/theme-youlog/releases/latest
# 获取 `"tag_name": "v0.1.0"` 中, v0.1.0 的值
# 拼接下载地址 https://github.com/everkm/theme-youlog/releases/download/v0.1.0/theme-youlog-v0.1.0.zip
# 解析压缩包, 获取 theme-youlog 文件

# echo "正在获取 theme-youlog 最新版本信息..."

# # 获取最新版本信息
# LATEST_RELEASE=$(curl -s https://api.github.com/repos/everkm/theme-youlog/releases/latest)

# # 提取 tag_name 中的版本号
# TAG_NAME=$(echo "$LATEST_RELEASE" | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4)
# VERSION=$(echo "$TAG_NAME" | sed 's/v//')
# echo "Theme-Youlog 最新版本: $VERSION"

# 构建下载地址
# https://github.com/everkm/theme-youlog/releases/download/v0.2.3/youlog.zip
DOWNLOAD_URL="https://github.com/everkm/theme-youlog/releases/download/v${THEME_YOULOG_VERSION}/youlog.zip"
wget --quiet "$DOWNLOAD_URL" -O "youlog.zip"

unzip "youlog.zip"

