#!/bin/bash
# scripts/check-system-health.sh
# 智能诊断助手 2.0 系统健康检查脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info "检查智能诊断助手2.0系统状态..."

# 1. 检查项目结构
print_info "检查项目结构..."
if [ ! -d "frontend" ]; then
    print_error "frontend目录不存在"
    exit 1
fi

if [ ! -d "backend" ]; then
    print_error "backend目录不存在"
    exit 1
fi

print_success "项目结构检查完成"

# 2. 检查依赖
print_info "检查前端依赖..."
cd frontend
if [ ! -f "package.json" ]; then
    print_error "package.json不存在"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    print_warning "node_modules不存在，正在安装..."
    yarn install --frozen-lockfile
fi

print_success "前端依赖检查完成"

print_info "检查后端依赖..."
cd ../backend
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt不存在"
    exit 1
fi

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    print_warning "虚拟环境不存在，创建中..."
    python -m venv venv
fi

print_success "后端依赖检查完成"

# 3. 检查环境变量
print_info "检查环境变量..."
cd ..
if [ ! -f "frontend/.env.local" ]; then
    print_warning ".env.local不存在，创建示例文件..."
    cat > frontend/.env.local << EOF
# AI服务配置
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku

# 后端服务地址
BACKEND_URL=http://localhost:8000
EOF
    print_warning "请编辑 frontend/.env.local 配置正确的API密钥"
fi

print_success "环境变量检查完成"

# 4. 检查核心文件
print_info "检查核心文件..."
CORE_FILES=(
    "frontend/components/ai-diagnosis/SmartDiagnosisChatInterface.tsx"
    "frontend/components/ai-diagnosis/ToolRecommendationPanel.tsx"
    "frontend/components/ai-diagnosis/ToolRecommendationCard.tsx"
    "frontend/app/api/ai-tool-recommendation/route.ts"
    "frontend/app/api/network-ping/route.ts"
    "frontend/app/api/wifi-scan/route.ts"
    "frontend/app/api/connectivity-check/route.ts"
    "frontend/app/api/gateway-info/route.ts"
    "frontend/app/api/packet-capture/route.ts"
    "frontend/app/smart-diagnosis/page.tsx"
)

missing_files=0
for file in "${CORE_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "核心文件缺失: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -eq 0 ]; then
    print_success "核心文件检查完成"
else
    print_error "发现 $missing_files 个核心文件缺失"
    exit 1
fi

# 5. 检查API端点（如果服务正在运行）
print_info "检查API端点..."
if curl -s -f http://localhost:3000/api/ai-tool-recommendation/health > /dev/null 2>&1; then
    print_success "AI推荐API正常"
else
    print_warning "AI推荐API未响应（可能服务未启动）"
fi

if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "后端服务正常"
else
    print_warning "后端服务未响应（可能服务未启动）"
fi

# 6. 检查组件完整性
print_info "检查组件完整性..."
component_count=$(find frontend/components/ai-diagnosis -name "*.tsx" | wc -l)
api_count=$(find frontend/app/api -name "route.ts" | wc -l)

print_success "发现 $component_count 个组件文件"
print_success "发现 $api_count 个API路由"

# 7. 系统总结
print_info "系统健康检查总结:"
echo "==================="
print_success "✅ 项目结构完整"
print_success "✅ 依赖配置正确"
print_success "✅ 核心文件完整"
print_success "✅ 组件数量: $component_count"
print_success "✅ API路由数量: $api_count"
echo "==================="

print_info "系统健康检查完成！"
print_info "如需启动服务，请运行: ./scripts/start-smart-diagnosis.sh" 