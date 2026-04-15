#!/bin/bash
# ============================================================
# ADADD 启动脚本 - 一键启动全栈服务
# ============================================================

set -e
cd "$(dirname "$0")"
echo ""
echo "╔══════════════════════════════════════╗"
echo "║  ADADD 广告行业资讯聚合平台 v2.0     ║"
echo "╚══════════════════════════════════════╝"
echo ""

VENV_DIR=".venv"
PYTHON="$VENV_DIR/bin/python3"

echo "[1/4] 检查环境..."
if [ ! -f "$PYTHON" ]; then
    echo "⚠️ 未找到虚拟环境，正在创建..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install flask flask-cors requests beautifulsoup4 lxml schedule -q
fi

echo "[2/4] 生成数据（220条全量资讯）..."
"$PYTHON" backend/generate_data.py

echo ""
echo "[3/4] 启动后端 API 服务 (Flask) ..."
echo "    → http://localhost:5000"
echo ""

# 启动 Flask 后端（后台运行）
"$PYTHON" backend/server.py &
FLASK_PID=$!
sleep 3

echo ""
echo "[4/4] 启动前端页面服务 (HTTP) ..."
echo "    → http://localhost:8190"
echo ""

# 启动静态文件服务器（前台运行，用于预览）
python3 -m http.server 8190 &
HTTP_PID=$!

echo "╔═════════════════════════════════════════╗"
echo "║  ✅ ADADD 已启动！                        ║"
echo "║                                          ║"
echo "║  前端页面: http://localhost:8190          ║"
echo "║  API接口:  http://localhost:5000/api/news ║"
echo "║  健康检查: http://localhost:5000/api/health║"
echo "║                                          ║"
echo "║  按 Ctrl+C 停止所有服务                   ║"
echo "╚═════════════════════════════════════════╝"
echo ""

# 等待中断信号
trap 'echo ""; echo "🛑 正在停止服务..."; kill $FLASK_PID $HTTP_PID 2>/dev/null; echo "✅ 所有服务已停止"; exit 0' INT TERM
wait