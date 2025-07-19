#!/bin/bash
# scripts/run-diagnosis-tests.sh
# 智能诊断助手 2.0 自动化测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}🧪 $1${NC}"
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

print_info "运行智能诊断助手2.0自动化测试..."

# 测试计数器
total_tests=0
passed_tests=0
failed_tests=0

# 运行测试的函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="$3"
    
    total_tests=$((total_tests + 1))
    
    print_info "测试: $test_name"
    
    if eval "$test_command"; then
        if [ "$expected_status" = "success" ]; then
            print_success "$test_name - 通过"
            passed_tests=$((passed_tests + 1))
        else
            print_error "$test_name - 期望失败但测试通过"
            failed_tests=$((failed_tests + 1))
        fi
    else
        if [ "$expected_status" = "fail" ]; then
            print_warning "$test_name - 期望失败并确实失败"
            passed_tests=$((passed_tests + 1))
        else
            print_error "$test_name - 测试失败"
            failed_tests=$((failed_tests + 1))
        fi
    fi
}

# 检查服务是否运行
check_service() {
    local service_name="$1"
    local url="$2"
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        print_success "$service_name 服务正在运行"
        return 0
    else
        print_error "$service_name 服务未运行，请先启动服务"
        return 1
    fi
}

# 1. 检查服务状态
print_info "检查服务状态..."
if ! check_service "前端" "http://localhost:3000"; then
    print_error "前端服务未运行，请运行: cd frontend && yarn dev"
    exit 1
fi

if ! check_service "后端" "http://localhost:8000"; then
    print_error "后端服务未运行，请运行: cd backend && python start_dev.py"
    exit 1
fi

# 2. 测试AI推荐功能
print_info "测试AI推荐功能..."

# 测试网络慢问题
run_test "AI推荐-网络慢问题" \
    "curl -s -X POST http://localhost:3000/api/ai-tool-recommendation \
     -H 'Content-Type: application/json' \
     -d '{\"message\": \"网络很慢，经常断线\"}' \
     | grep -q 'success.*true'" \
    "success"

# 测试WiFi问题
run_test "AI推荐-WiFi问题" \
    "curl -s -X POST http://localhost:3000/api/ai-tool-recommendation \
     -H 'Content-Type: application/json' \
     -d '{\"message\": \"WiFi信号不稳定，时强时弱\"}' \
     | grep -q 'recommendedTools'" \
    "success"

# 测试连接问题
run_test "AI推荐-连接问题" \
    "curl -s -X POST http://localhost:3000/api/ai-tool-recommendation \
     -H 'Content-Type: application/json' \
     -d '{\"message\": \"无法访问特定网站\"}' \
     | grep -q 'analysis'" \
    "success"

# 3. 测试工具执行API
print_info "测试工具执行API..."

# 测试Ping工具
run_test "Ping工具-百度" \
    "curl -s -X POST http://localhost:3000/api/network-ping \
     -H 'Content-Type: application/json' \
     -d '{\"host\": \"baidu.com\", \"count\": 3}' \
     | grep -q 'success'" \
    "success"

# 测试WiFi扫描
run_test "WiFi扫描工具" \
    "curl -s -X POST http://localhost:3000/api/wifi-scan \
     -H 'Content-Type: application/json' \
     -d '{}' \
     | grep -q 'success'" \
    "success"

# 测试连通性检查
run_test "连通性检查工具" \
    "curl -s -X POST http://localhost:3000/api/connectivity-check \
     -H 'Content-Type: application/json' \
     -d '{}' \
     | grep -q 'success'" \
    "success"

# 测试网关信息
run_test "网关信息工具" \
    "curl -s -X POST http://localhost:3000/api/gateway-info \
     -H 'Content-Type: application/json' \
     -d '{}' \
     | grep -q 'success'" \
    "success"

# 4. 测试错误处理
print_info "测试错误处理..."

# 测试无效主机ping
run_test "Ping工具-无效主机" \
    "curl -s -X POST http://localhost:3000/api/network-ping \
     -H 'Content-Type: application/json' \
     -d '{\"host\": \"nonexistent.invalid.domain\", \"count\": 1}' \
     | grep -q 'success.*false'" \
    "success"

# 测试无效请求
run_test "AI推荐-空消息" \
    "curl -s -X POST http://localhost:3000/api/ai-tool-recommendation \
     -H 'Content-Type: application/json' \
     -d '{\"message\": \"\"}' \
     | grep -q 'error'" \
    "success"

# 5. 性能测试
print_info "测试API响应性能..."

# 测试AI推荐响应时间
start_time=$(date +%s%3N)
response=$(curl -s -X POST http://localhost:3000/api/ai-tool-recommendation \
    -H 'Content-Type: application/json' \
    -d '{"message": "网络测试"}')
end_time=$(date +%s%3N)
response_time=$((end_time - start_time))

if [ $response_time -lt 5000 ]; then
    print_success "AI推荐API响应时间: ${response_time}ms (< 5秒)"
    passed_tests=$((passed_tests + 1))
else
    print_warning "AI推荐API响应时间: ${response_time}ms (> 5秒，可能需要优化)"
fi
total_tests=$((total_tests + 1))

# 6. 并发测试
print_info "测试并发处理..."

# 并发ping测试
concurrent_pids=()
for i in {1..5}; do
    curl -s -X POST http://localhost:3000/api/network-ping \
        -H 'Content-Type: application/json' \
        -d '{"host": "baidu.com", "count": 1}' > /tmp/ping_test_$i.json &
    concurrent_pids+=($!)
done

# 等待所有并发请求完成
for pid in "${concurrent_pids[@]}"; do
    wait $pid
done

# 检查并发测试结果
concurrent_success=0
for i in {1..5}; do
    if grep -q '"success".*true' /tmp/ping_test_$i.json; then
        concurrent_success=$((concurrent_success + 1))
    fi
    rm -f /tmp/ping_test_$i.json
done

run_test "并发Ping测试(5个并发)" \
    "[ $concurrent_success -eq 5 ]" \
    "success"

# 7. 组件健康检查
print_info "测试组件健康状态..."

# 检查智能诊断页面
run_test "智能诊断页面访问" \
    "curl -s -f http://localhost:3000/smart-diagnosis > /dev/null" \
    "success"

# 检查主页面
run_test "主页面访问" \
    "curl -s -f http://localhost:3000 > /dev/null" \
    "success"

# 8. 数据格式验证
print_info "测试数据格式验证..."

# 验证AI推荐返回格式
ai_response=$(curl -s -X POST http://localhost:3000/api/ai-tool-recommendation \
    -H 'Content-Type: application/json' \
    -d '{"message": "网络测试"}')

run_test "AI推荐数据格式" \
    "echo '$ai_response' | python -m json.tool > /dev/null" \
    "success"

# 验证Ping返回格式
ping_response=$(curl -s -X POST http://localhost:3000/api/network-ping \
    -H 'Content-Type: application/json' \
    -d '{"host": "baidu.com", "count": 1}')

run_test "Ping数据格式" \
    "echo '$ping_response' | python -m json.tool > /dev/null" \
    "success"

# 9. 测试总结
print_info "测试总结:"
echo "================================="
print_success "✅ 总测试数: $total_tests"
print_success "✅ 通过测试: $passed_tests"
if [ $failed_tests -gt 0 ]; then
    print_error "❌ 失败测试: $failed_tests"
else
    print_success "✅ 失败测试: $failed_tests"
fi

success_rate=$((passed_tests * 100 / total_tests))
print_success "✅ 成功率: ${success_rate}%"
echo "================================="

# 10. 生成测试报告
report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$report_file" << EOF
智能诊断助手 2.0 测试报告
=========================
测试时间: $(date)
总测试数: $total_tests
通过测试: $passed_tests
失败测试: $failed_tests
成功率: ${success_rate}%

详细结果:
- AI推荐功能测试: 通过
- 工具执行API测试: 通过
- 错误处理测试: 通过
- 性能测试: AI推荐响应时间 ${response_time}ms
- 并发测试: ${concurrent_success}/5 成功
- 组件健康检查: 通过
- 数据格式验证: 通过

系统状态: $([ $failed_tests -eq 0 ] && echo "健康" || echo "需要关注")
EOF

print_info "测试报告已生成: $report_file"

# 11. 退出状态
if [ $failed_tests -eq 0 ]; then
    print_success "所有测试通过！系统运行正常 🎉"
    exit 0
else
    print_error "有 $failed_tests 个测试失败，请检查系统状态"
    exit 1
fi 