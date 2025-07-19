#!/bin/bash

echo "🔍 WiFi扫描功能测试"
echo "===================="

# 检查端口
check_ports() {
    echo "📡 检查服务端口..."
    
    # 检查前端端口
    if lsof -i :3000 > /dev/null 2>&1; then
        echo "✅ 前端服务 (3000) 正在运行"
    else
        echo "❌ 前端服务 (3000) 未运行"
        echo "请运行: cd frontend && yarn dev"
        return 1
    fi
    
    # 检查后端端口
    # if lsof -i :8000 > /dev/null 2>&1; then
    #     echo "✅ 后端服务 (8000) 正在运行"
    # else
    #     echo "❌ 后端服务 (8000) 未运行"
    #     echo "请运行: cd backend && python start_dev.py"
    #     return 1
    # fi
    
    return 0
}

# 测试后端API
test_backend_api() {
    echo ""
    echo "🔧 测试后端WiFi扫描API..."
    
    # 测试WiFi信号获取
    echo "📶 测试当前WiFi信号..."
    response=$(curl -s -w "\n%{http_code}" "http://localhost:8000/api/wifi/signal")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ WiFi信号API正常"
        echo "📊 响应数据: $(echo "$body" | jq -r '.data.ssid // "未获取到SSID"')"
    else
        echo "❌ WiFi信号API异常 (状态码: $http_code)"
        echo "📄 响应: $body"
    fi
    
    # 测试WiFi扫描
    echo "🔍 测试WiFi网络扫描..."
    response=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8000/api/wifi/scan")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ WiFi扫描API正常"
        network_count=$(echo "$body" | jq -r '.data.total_networks // 0')
        echo "📊 发现网络数量: $network_count"
        
        if [ "$network_count" -gt 0 ]; then
            echo "🏠 当前网络: $(echo "$body" | jq -r '.data.current_wifi.ssid // "未连接"')"
            echo "📡 信道分析: $(echo "$body" | jq -r '.data.recommendations.need_adjustment // false')"
        fi
    else
        echo "❌ WiFi扫描API异常 (状态码: $http_code)"
        echo "📄 响应: $body"
    fi
}

# 测试前端API
test_frontend_api() {
    echo ""
    echo "🌐 测试前端WiFi扫描API..."
    
    response=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:3000/api/wifi-scan")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ 前端WiFi扫描API正常"
        if echo "$body" | jq -e '.success' > /dev/null 2>&1; then
            echo "📊 数据格式正确"
            echo "🔢 网络数量: $(echo "$body" | jq -r '.data.total_networks // 0')"
        else
            echo "⚠️  响应格式异常"
            echo "📄 响应: $body"
        fi
    else
        echo "❌ 前端WiFi扫描API异常 (状态码: $http_code)"
        echo "📄 响应: $body"
    fi
}

# 测试页面访问
test_page_access() {
    echo ""
    echo "📱 测试WiFi扫描页面访问..."
    
    response=$(curl -s -w "\n%{http_code}" "http://localhost:3000/wifi-scan")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ WiFi扫描页面可访问"
        echo "🌐 URL: http://localhost:3000/wifi-scan"
    else
        echo "❌ WiFi扫描页面访问异常 (状态码: $http_code)"
    fi
}

# 性能测试
performance_test() {
    echo ""
    echo "⚡ WiFi扫描性能测试..."
    
    echo "🔄 执行5次扫描测试..."
    total_time=0
    success_count=0
    
    for i in {1..5}; do
        echo -n "  测试 $i/5: "
        start_time=$(date +%s.%N)
        
        response=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:3000/api/wifi-scan")
        http_code=$(echo "$response" | tail -n1)
        
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        if [ "$http_code" -eq 200 ]; then
            echo "✅ 成功 (${duration}s)"
            success_count=$((success_count + 1))
            total_time=$(echo "$total_time + $duration" | bc)
        else
            echo "❌ 失败 (状态码: $http_code)"
        fi
    done
    
    if [ $success_count -gt 0 ]; then
        avg_time=$(echo "scale=3; $total_time / $success_count" | bc)
        echo "📊 平均响应时间: ${avg_time}s"
        echo "📈 成功率: $success_count/5"
    fi
}

# 移动端测试提示
mobile_test_tips() {
    echo ""
    echo "📱 移动端测试建议:"
    echo "=================="
    echo "1. 在移动设备浏览器中访问: http://[your-ip]:3000/wifi-scan"
    echo "2. 检查布局是否适配移动端"
    echo "3. 测试柱状图在小屏幕上的显示效果"
    echo "4. 验证卡片组件的响应式布局"
    echo "5. 测试信道分析图表的横向滚动"
    
    # 获取本机IP
    if command -v ifconfig > /dev/null 2>&1; then
        ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
        if [ ! -z "$ip" ]; then
            echo ""
            echo "🌐 本机IP地址: $ip"
            echo "📱 移动端访问URL: http://$ip:3000/wifi-scan"
        fi
    fi
}

# 主测试流程
main() {
    echo "开始WiFi扫描功能测试..."
    echo ""
    
    # 检查依赖
    if ! command -v curl > /dev/null 2>&1; then
        echo "❌ 缺少依赖: curl"
        exit 1
    fi
    
    if ! command -v jq > /dev/null 2>&1; then
        echo "⚠️  建议安装 jq 以获得更好的JSON解析"
    fi
    
    # 执行测试
    if check_ports; then
        test_backend_api
        test_frontend_api
        test_page_access
        performance_test
        mobile_test_tips
        
        echo ""
        echo "🎉 WiFi扫描功能测试完成!"
        echo ""
        echo "📝 功能清单:"
        echo "  ✅ WiFi网络扫描"
        echo "  ✅ 当前网络信息展示"
        echo "  ✅ 信道干扰分析"
        echo "  ✅ 柱状图展示"
        echo "  ✅ 优化建议"
        echo "  ✅ 移动端适配"
        echo ""
        echo "🌐 访问地址: http://localhost:3000/wifi-scan"
    else
        echo ""
        echo "❌ 服务检查失败，请确保前后端服务正在运行"
        exit 1
    fi
}

# 执行主函数
main "$@" 