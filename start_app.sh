#!/bin/bash

VENV_DIR=".venv"
GUNICORN_WORKERS=4
GUNICORN_PORT=8000
WSGI_FILE="app"

source $VENV_DIR/bin/activate

echo "启动 Gunicorn 服务器..."
gunicorn -w $GUNICORN_WORKERS -b 0.0.0.0:$GUNICORN_PORT $WSGI_FILE:app &

# 获取 Gunicorn 进程 ID
GUNICORN_PID=$!
echo "Gunicorn 已启动 (PID: $GUNICORN_PID)"
echo "应用运行在: http://0.0.0.0:$GUNICORN_PORT"
