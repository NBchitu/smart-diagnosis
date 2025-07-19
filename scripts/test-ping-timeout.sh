#!/bin/bash

# Ping 超时错误修复测试脚本
# 测试各种ping场景，验证前端不会崩溃

echo "🧪 开始测试 Ping 超时错误修复..."
echo "========================================"

# 检查前端服务是否运行
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ 前端服务未运行，请先启动: cd frontend && yarn dev"
    exit 1
fi

# 检查后端服务是否运行
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ 后端服务未运行，请先启动: cd backend && python start_dev.py"
    exit 1
fi

echo "✅ 前端和后端服务都在运行"
echo ""

# 测试函数
test_ping() {
    local host=$1
    local description=$2
    
    echo "🔍 测试: $description"
    echo "目标主机: $host"
    
    # 发送ping请求
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"host\": \"$host\", \"count\": 3}" \
        http://localhost:3000/api/network-ping)
    
    if [ $? -eq 0 ]; then
        echo "✅ API请求成功"
        # 检查返回数据结构
        if echo "$response" | jq -e '.status' > /dev/null; then
            echo "✅ 返回数据格式正确"
            
            # 检查是否包含必要字段
            success=$(echo "$response" | jq -r '.data.success // false')
            host_field=$(echo "$response" | jq -r '.data.host // "unknown"')
            
            echo "   - 主机: $host_field"
            echo "   - 成功: $success"
            
            # 如果成功，检查时间字段
            if [ "$success" = "true" ]; then
                avg_time=$(echo "$response" | jq -r '.data.avg_time // null')
                if [ "$avg_time" != "null" ]; then
                    echo "   - 平均延迟: ${avg_time}ms"
                else
                    echo "   - ⚠️ 平均延迟字段缺失"
                fi
            else
                echo "   - ℹ️ Ping失败，这是正常的"
            fi
        else
            echo "❌ 返回数据格式错误"
        fi
    else
        echo "❌ API请求失败"
    fi
    
    echo ""
}

# 测试场景1：正常可达主机
echo "📋 测试场景1: 正常可达主机"
test_ping "baidu.com" "测试正常访问"

# 测试场景2：超时主机（通常被墙）
echo "📋 测试场景2: 超时主机"
test_ping "google.com" "测试超时情况"

# 测试场景3：不存在的主机
echo "📋 测试场景3: 不存在的主机"
test_ping "nonexistent-host-12345.com" "测试不存在主机"

# 测试场景4：IP地址
echo "📋 测试场景4: IP地址"
test_ping "8.8.8.8" "测试IP地址"

# 测试场景5：本地主机
echo "📋 测试场景5: 本地主机"
test_ping "localhost" "测试本地主机"

echo "========================================"
echo "✅ 所有测试完成"
echo ""
echo "📝 测试说明："
echo "- 如果没有看到错误，说明修复成功"
echo "- 超时和失败的情况应该正常处理，不会崩溃"
echo "- 前端组件应该显示 '--' 而不是undefined"
echo ""
echo "🌐 打开浏览器访问 http://localhost:3000/smart-diagnosis"
echo "   手动测试步进式诊断功能" 