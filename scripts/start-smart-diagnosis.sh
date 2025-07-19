#!/bin/bash

# 智能诊断助手 2.0 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "\n${PURPLE}================================================${NC}"
    echo -e "${PURPLE}        智能诊断助手 2.0 启动工具${NC}"
    echo -e "${PURPLE}================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

main() {
    print_header
    
    print_info "正在启动智能诊断助手 2.0..."
    
    # 检查后端服务
    if check_port 8000; then
        print_success "后端服务已运行 (端口 8000)"
    else
        print_info "启动后端服务..."
        cd backend && python start_dev.py &
        sleep 3
    fi
    
    # 检查前端服务
    if check_port 3000; then
        print_success "前端服务已运行 (端口 3000)"
    else
        print_info "启动前端服务..."
        cd frontend && yarn dev &
        sleep 5
    fi
    
    echo -e "\n${GREEN}🎉 智能诊断助手 2.0 启动完成！${NC}\n"
    echo -e "${YELLOW}📱 访问地址: ${BLUE}http://localhost:3000/smart-diagnosis${NC}"
    echo -e "${YELLOW}🧪 测试示例: ${NC}\"网络连接很慢，打开网页要等很久\""
    
    echo -e "\n${GREEN}按 Ctrl+C 停止服务${NC}"
    wait
}

main "$@" 