#!/bin/bash

# AI SDK v5 + MCP 集成测试启动脚本
# 用于启动所有必要的服务来测试新功能

echo "🚀 启动 AI SDK v5 + MCP 集成测试环境"
echo "==========================================="

# 检查是否在正确的目录
if [ ! -f "frontend/package.json" ]; then
  echo "❌ 请在项目根目录运行此脚本"
  exit 1
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印状态
print_status() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python MCP 服务器
print_status "检查 Python MCP 服务器..."

# 检查必要的 Python 文件
mcp_servers=(
  "backend/app/mcp/servers/ping_server_fixed.py"
  "backend/app/mcp/servers/wifi_server.py"
  "backend/app/mcp/servers/connectivity_server.py"
  "backend/app/mcp/servers/gateway_server.py"
  "backend/app/mcp/servers/packet_capture_server.py"
)

missing_servers=()
for server in "${mcp_servers[@]}"; do
  if [ ! -f "$server" ]; then
    missing_servers+=("$server")
  fi
done

if [ ${#missing_servers[@]} -gt 0 ]; then
  print_warning "发现缺失的 MCP 服务器文件:"
  for server in "${missing_servers[@]}"; do
    echo "  - $server"
  done
  print_warning "AI SDK v5 集成可能无法完全工作"
fi

# 检查 Node.js 前端
print_status "检查 Node.js 前端环境..."

cd frontend

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
  print_warning "Node.js 依赖未安装，正在安装..."
  yarn install
fi

# 检查 AI SDK 版本
ai_version=$(node -e "console.log(require('./package.json').dependencies.ai)")
print_success "AI SDK 版本: $ai_version"

# 检查环境变量
print_status "检查环境变量..."

if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
  print_error "未找到 AI API 密钥!"
  print_error "请设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY 环境变量"
  exit 1
fi

if [ ! -z "$OPENROUTER_API_KEY" ]; then
  print_success "找到 OpenRouter API 密钥"
fi

if [ ! -z "$OPENAI_API_KEY" ]; then
  print_success "找到 OpenAI API 密钥"
fi

# 启动开发服务器
print_status "启动 Next.js 开发服务器..."
print_status "前端地址: http://localhost:3000"
print_status "测试页面: http://localhost:3000/test-ai-v5"

echo ""
echo "🧪 测试指南:"
echo "============"
echo "1. 访问 http://localhost:3000/test-ai-v5"
echo "2. 尝试以下测试命令:"
echo "   • ping baidu.com"
echo "   • 扫描WiFi网络"
echo "   • 检查网络连通性"
echo "   • 抓包分析 sina.com"
echo "   • 查看网关信息"
echo ""
echo "3. 观察控制台日志以查看 MCP 工具调用"
echo "4. 检查是否显示 '工具调用' 消息类型"
echo ""
echo "💡 如果遇到问题:"
echo "   • 检查 backend Python 服务器是否运行"
echo "   • 查看浏览器控制台错误"
echo "   • 检查 API 密钥配置"
echo ""

# 启动服务器
yarn dev 