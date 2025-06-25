#!/bin/bash

set -e

REPO=git@github.com:jcold/youlog-dayu.git
TAG=youlog-www@v0.1.1
SRC_DIR=youlog-www
YOULOG_VERSION=0.1.1

cd /Users/dayu/tmp/cicd

export PATH=/Users/dayu/tmp/cicd:$PATH

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



/Users/dayu/Coder/everkm/everkm2/be/everkm-publish/target/debug/everkm-publish serve \
		--work-dir ./src/$SRC_DIR \
		--base-prefix /dayu/haowen/v${YOULOG_VERSION}/ \
		--cdn-prefix https://assets.daobox.cc/yl-member/dayu/haowen/ \
		--theme-dir youlog \
		--export





