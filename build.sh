#!/bin/bash

set -e

if [ $# -ne 6 ]; then
    echo "用法: $0 <member> <youlog> <version> <repo> <tag> <sub_dir>"
    echo "示例: $0 dayu haowen 0.0.1 https://github.com/jcold/youlog-press.git haowen@v0.0.1 haowen"
    exit 1
fi

MEMBER="$1"
YOULOG="$2"
YOULOG_VERSION="$3"

REPO="$4"
TAG="$5"
SUB_DIR="$6"

CURRENT_DIR=$(pwd)
BUILD_DIR="$CURRENT_DIR/tmp"

if [ ! -d "$BUILD_DIR" ]; then
    echo "BUILD_DIR 不存在，请先运行 setup_env.sh"
    exit 1
fi

cd $BUILD_DIR
echo "当前目录: $CURRENT_DIR"
CURRENT_DIR=$(pwd)

export PATH=$CURRENT_DIR:$PATH

# 克隆指定 tag 到 src 目录
echo "正在克隆 tag: $TAG 到 src 目录..."
if [ -d "src" ]; then
    rm -rf src
fi
git clone --depth 1 --single-branch --branch $TAG $REPO src

# 检查克隆是否成功
if [ $? -eq 0 ]; then
    echo "成功克隆 tag $TAG 到 src 目录"
    
    # 进入 src 目录并创建新分支
    cd src
    echo "基于 tag $TAG 创建新分支: $TAG-branch"
    git checkout -b $TAG-branch
    
    # 验证当前状态
    echo "当前分支: $(git branch --show-current)"
    echo "当前 HEAD: $(git rev-parse HEAD)"
    echo "当前 tag: $(git describe --tags --exact-match HEAD 2>/dev/null || echo '不是精确的 tag')"
    cd ..
else
    echo "克隆失败，请检查 tag 名称和仓库地址"
    exit 1
fi



export EVERKM_LOG=error

everkm-publish serve \
		--work-dir ./src/$SUB_DIR \
		--base-prefix /$MEMBER/$YOULOG/v${YOULOG_VERSION}/ \
		--cdn-prefix https://assets.daobox.cc/yl-member/$MEMBER/$YOULOG/ \
		--theme-dir ./youlog \
        --dist-dir $CURRENT_DIR/dist-pages \
		--export





