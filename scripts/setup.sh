#!/bin/bash
set -e

echo "=== 攀岩视频分析系统 - 环境配置 ==="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js 20+"
    exit 1
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "错误: 未找到 FFmpeg，请先安装 FFmpeg"
    echo "  Windows: winget install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    exit 1
fi

echo "✓ 环境检查通过"

# Setup backend
echo ""
echo "--- 配置后端 ---"
cd backend
python -m venv .venv 2>/dev/null || python3 -m venv .venv
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -r requirements.txt
echo "✓ 后端依赖安装完成"

# Copy .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ 已创建 .env 文件，请编辑填入 ANTHROPIC_API_KEY"
fi

cd ..

# Setup frontend
echo ""
echo "--- 配置前端 ---"
cd frontend
npm install
echo "✓ 前端依赖安装完成"

cd ..

echo ""
echo "=== 配置完成 ==="
echo ""
echo "启动方式:"
echo "  终端1 (后端): cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "  终端2 (前端): cd frontend && npm run dev"
echo ""
echo "然后访问 http://localhost:3000"
