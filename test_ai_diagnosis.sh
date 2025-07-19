#!/bin/bash

echo "🚀 开始测试AI诊断系统..."

# 测试后端ping功能
echo "🔍 测试后端ping功能..."
curl -s -X POST http://localhost:8000/api/network/ping_test \
  -H "Content-Type: application/json" \
  -d '{"host": "baidu.com", "count": 3}' | jq '.' 2>/dev/null || echo "后端ping测试失败"

echo ""
echo "==================================================="
echo ""

# 测试AI诊断功能
echo "🔍 测试AI诊断功能..."
response=$(curl -s -X POST http://localhost:3000/api/ai-diagnosis \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "网络连接不稳定，经常断线"}]}' \
  -w "HTTP_STATUS:%{http_code}")

# 提取HTTP状态码
http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
response_body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')

echo "📊 响应状态: $http_status"

if [ "$http_status" = "200" ]; then
    echo "✅ API调用成功"
    
    # 检查响应内容
    if echo "$response_body" | grep -q "网络\|连接\|ping"; then
        echo "✅ AI诊断功能正常工作"
    else
        echo "⚠️ AI诊断功能可能存在问题"
    fi
    
    echo "📝 响应内容片段:"
    echo "$response_body" | head -c 300
    echo "..."
    
else
    echo "❌ API调用失败: $http_status"
    echo "错误详情: $response_body"
fi

echo ""
echo "✅ 测试完成" 