#!/bin/bash

# 设置错误时退出
set -e

# 检查参数
if [ $# -ne 3 ]; then
    echo "用法: $0 <member> <youlog> <version>"
    echo "示例: $0 dayu haowen 0.0.1"
    exit 1
fi

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

MEMBER="$1"
YOULOG="$2"
VERSION="$3"

TARGET_DIR="$BUILD_DIR/dist-pages"


ZIP_NAME="${YOULOG}@${VERSION}.zip"
YOULOG_DIR="$MEMBER/$YOULOG"
VERSION_DIR="${YOULOG_DIR}/v$VERSION"


echo "开始处理目录: $TARGET_DIR"

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误: 目录 '$TARGET_DIR' 不存在"
    exit 1
fi


# 如果 QINIU_ACCESS_KEY 和 QINIU_SECRET_KEY 未设置，则使用 qshell 登录
if [ -z "$QINIU_ACCESS_KEY" ] && [ -z "$QINIU_SECRET_KEY" ]; then
    qshell account $QINIU_ACCESS_KEY $QINIU_SECRET_KEY everkm -w
fi

# 上传CDN
qshell qupload2 \
    --src-dir=$TARGET_DIR/assets/ \
    --key-prefix=yl-member/$YOULOG_DIR/assets/ \
    --bucket=dayu-assets \
    --thread-count 5 \
    --overwrite \
    --check-hash  \
    --rescan-local=true \
    --skip-fixed-strings=.DS_Store


# 第一步：压缩所有 HTML 文件为 .html.gz，保持目录结构，然后删除源文件
echo "第一步：压缩所有 HTML 文件并删除源文件..."

# 查找所有 HTML 文件并压缩
find "$TARGET_DIR" -name "*.html" -type f | while read -r file; do
    echo "处理文件: $file"

    gzip -c "$file" > "$file.gz"
    
    # 删除源 HTML 文件
    rm "$file"
done


# 第二步：将整个目标目录打包为 zip 文件，使用 Stored 模式（不压缩）
echo "第二步：打包 $TARGET_DIR/$VERSION_DIR 目录为 zip 文件..."

# 删除已存在的 zip 文件（如果存在）
if [ -f "$CURRENT_DIR/$ZIP_NAME" ]; then
    echo "删除已存在的 $CURRENT_DIR/$ZIP_NAME 文件"
    rm -f "$CURRENT_DIR/$ZIP_NAME"
fi

# 使用 zip 命令打包，-0 参数表示使用 Stored 模式（不压缩）
# 从目标目录内部开始打包，这样 zip 文件中不会包含目标目录名
echo "打包 $TARGET_DIR/$VERSION_DIR 目录为 $CURRENT_DIR/$ZIP_NAME"
cd "$TARGET_DIR"/$VERSION_DIR/ && zip -0 -r "$CURRENT_DIR/$ZIP_NAME" . && cd $CURRENT_DIR

echo "打包完成！"

# 显示统计信息
echo ""
echo "统计信息:"
echo "压缩后的 .html.gz 文件数量: $(find "$TARGET_DIR" -name "*.html.gz" -type f | wc -l)"
echo "$ZIP_NAME 文件大小: $(du -h "$CURRENT_DIR/$ZIP_NAME" | cut -f1)"
echo "ZIP 文件位置: $CURRENT_DIR/$ZIP_NAME"

