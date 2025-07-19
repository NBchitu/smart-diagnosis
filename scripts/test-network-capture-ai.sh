#!/bin/bash

# 网络抓包与AI分析系统测试脚本
# 用于启动和测试完整的网络抓包AI分析流程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}🚀 网络抓包与AI分析系统测试${NC}"
echo "项目根目录: $PROJECT_ROOT"

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}📋 检查系统依赖...${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    
    # 检查tcpdump
    if ! command -v tcpdump &> /dev/null; then
        echo -e "${RED}❌ tcpdump 未安装，请运行: sudo apt-get install tcpdump${NC}"
        exit 1
    fi
    
    # 检查sudo权限
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}⚠️ 需要sudo权限来运行tcpdump${NC}"
        echo "请确保当前用户有sudo权限，或者运行: sudo visudo"
    fi
    
    echo -e "${GREEN}✅ 系统依赖检查完成${NC}"
}

# 安装Python依赖
install_python_deps() {
    echo -e "${YELLOW}📦 安装Python依赖...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ Python依赖安装完成${NC}"
}

# 安装Node.js依赖
install_node_deps() {
    echo -e "${YELLOW}📦 安装Node.js依赖...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 检查package.json
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ 前端package.json不存在${NC}"
        exit 1
    fi
    
    # 安装依赖
    if command -v yarn &> /dev/null; then
        yarn install
    else
        npm install
    fi
    
    echo -e "${GREEN}✅ Node.js依赖安装完成${NC}"
}

# 检查AI配置
check_ai_config() {
    echo -e "${YELLOW}🤖 检查AI配置...${NC}"
    
    # 检查环境变量
    if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${YELLOW}⚠️ 未检测到AI API密钥${NC}"
        echo "请设置以下环境变量之一:"
        echo "  export OPENROUTER_API_KEY='your-key'"
        echo "  export OPENAI_API_KEY='your-key'"
        echo "  export ANTHROPIC_API_KEY='your-key'"
        echo ""
        echo "或者创建 .env 文件包含相应配置"
        
        # 检查.env文件
        if [ -f "$PROJECT_ROOT/.env" ]; then
            echo "发现.env文件，尝试加载..."
            source "$PROJECT_ROOT/.env"
        fi
    else
        echo -e "${GREEN}✅ AI配置检查完成${NC}"
    fi
}

# 启动后端服务
start_backend() {
    echo -e "${YELLOW}🔧 启动后端服务...${NC}"
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 检查端口是否被占用
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️ 端口8000已被占用，尝试停止现有服务...${NC}"
        pkill -f "uvicorn.*8000" || true
        sleep 2
    fi
    
    # 启动服务
    echo "启动FastAPI服务..."
    python start_dev.py &
    BACKEND_PID=$!
    
    # 等待服务启动
    echo "等待后端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务启动成功${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    return 1
}

# 启动前端服务
start_frontend() {
    echo -e "${YELLOW}🌐 启动前端服务...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 检查端口是否被占用
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️ 端口3000已被占用，尝试停止现有服务...${NC}"
        pkill -f "next.*3000" || true
        sleep 2
    fi
    
    # 启动服务
    echo "启动Next.js服务..."
    if command -v yarn &> /dev/null; then
        yarn dev &
    else
        npm run dev &
    fi
    FRONTEND_PID=$!
    
    # 等待服务启动
    echo "等待前端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务启动成功${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ 前端服务启动失败${NC}"
    return 1
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}🧪 运行系统测试...${NC}"
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 运行测试脚本
    python test_network_capture_ai.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 所有测试通过${NC}"
    else
        echo -e "${RED}❌ 部分测试失败${NC}"
        return 1
    fi
}

# 清理函数
cleanup() {
    echo -e "${YELLOW}🧹 清理进程...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # 清理可能残留的进程
    pkill -f "uvicorn.*8000" 2>/dev/null || true
    pkill -f "next.*3000" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 主函数
main() {
    # 设置清理陷阱
    trap cleanup EXIT
    
    echo -e "${BLUE}开始网络抓包与AI分析系统测试流程${NC}"
    
    # 检查依赖
    check_dependencies
    
    # 安装依赖
    install_python_deps
    install_node_deps
    
    # 检查AI配置
    check_ai_config
    
    # 启动服务
    if start_backend; then
        echo -e "${GREEN}后端服务运行在: http://localhost:8000${NC}"
    else
        echo -e "${RED}后端服务启动失败${NC}"
        exit 1
    fi
    
    if start_frontend; then
        echo -e "${GREEN}前端服务运行在: http://localhost:3000${NC}"
    else
        echo -e "${RED}前端服务启动失败${NC}"
        exit 1
    fi
    
    # 等待用户确认
    echo ""
    echo -e "${BLUE}🎯 服务已启动，现在可以进行测试${NC}"
    echo "1. 自动运行测试脚本"
    echo "2. 手动测试前端界面"
    echo "3. 退出"
    
    read -p "请选择操作 (1-3): " choice
    
    case $choice in
        1)
            run_tests
            ;;
        2)
            echo -e "${GREEN}请在浏览器中访问: http://localhost:3000/network-capture-ai-test${NC}"
            echo "按任意键退出..."
            read -n 1
            ;;
        3)
            echo "退出测试"
            ;;
        *)
            echo "无效选择，退出"
            ;;
    esac
}

# 运行主函数
main "$@"
