#!/bin/bash

# 定义变量
APP_NAME="log-trace-finder-app"
VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"

echo "开始部署应用: $APP_NAME"

# 1. 检查 Python 版本
echo "检查 Python 版本..."
python3 --version || { echo "Python3 未安装"; exit 1; }

# 2. 创建虚拟环境
echo "创建虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
    echo "虚拟环境已创建"
else
    echo "虚拟环境已存在，跳过创建"
fi

# 3. 激活虚拟环境
echo "激活虚拟环境..."
source $VENV_DIR/bin/activate

# 4. 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 5. 安装依赖
echo "安装依赖..."
if [ -f "$REQUIREMENTS" ]; then
    pip install -r $REQUIREMENTS
else
    echo "未找到 $REQUIREMENTS 文件，将安装 Flask 和 Gunicorn"
    pip install flask gunicorn
fi
pip install gunicorn
echo "环境初始化完成!"
