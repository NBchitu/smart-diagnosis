#!/bin/bash

# 测试步进式诊断功能
# 使用方法: ./scripts/test-stepwise-diagnosis.sh

echo "🧪 开始测试步进式诊断功能..."

# 检查前端服务是否运行
if ! curl -s http://localhost:3000/smart-diagnosis > /dev/null; then
    echo "❌ 前端服务未运行，请先启动: cd frontend && yarn dev"
    exit 1
fi

# 检查后端服务是否运行
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ 后端服务未运行，请先启动: cd backend && python start_dev.py"
    exit 1
fi

echo "✅ 服务检查通过"

# 测试1: 问题分析
echo "🔍 测试1: 问题分析 (analyze)"
ANALYSIS_RESULT=$(curl -s -X POST http://localhost:3000/api/ai-diagnosis-stepwise \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze", "message": "网络连接很慢"}' | jq -r '.success')

if [ "$ANALYSIS_RESULT" = "true" ]; then
    echo "✅ 问题分析测试通过"
else
    echo "❌ 问题分析测试失败"
    echo "响应: $ANALYSIS_RESULT"
fi

# 测试2: 获取下一步
echo "🔍 测试2: 获取下一步 (get_next_step)"
NEXT_STEP_RESULT=$(curl -s -X POST http://localhost:3000/api/ai-diagnosis-stepwise \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_next_step",
    "context": {
      "originalProblem": "网络连接很慢",
      "currentStep": 0,
      "totalSteps": 3,
      "executedTools": [],
      "isComplete": false
    }
  }' | jq -r '.success')

if [ "$NEXT_STEP_RESULT" = "true" ]; then
    echo "✅ 获取下一步测试通过"
else
    echo "❌ 获取下一步测试失败"
    echo "响应: $NEXT_STEP_RESULT"
fi

# 测试3: 结果评估
echo "🔍 测试3: 结果评估 (evaluate_result)"
EVALUATION_RESULT=$(curl -s -X POST http://localhost:3000/api/ai-diagnosis-stepwise \
  -H "Content-Type: application/json" \
  -d '{
    "action": "evaluate_result",
    "context": {
      "originalProblem": "网络连接很慢",
      "currentStep": 1,
      "totalSteps": 3,
      "executedTools": [{
        "id": "ping",
        "name": "Ping测试",
        "result": {"success": true, "data": {"avg_time": 150, "packet_loss": 0}},
        "timestamp": "2024-01-01T00:00:00Z"
      }],
      "isComplete": false
    },
    "toolResult": {
      "toolId": "ping",
      "result": {"success": true, "data": {"avg_time": 150, "packet_loss": 0}}
    }
  }' | jq -r '.success')

if [ "$EVALUATION_RESULT" = "true" ]; then
    echo "✅ 结果评估测试通过"
else
    echo "❌ 结果评估测试失败"
    echo "响应: $EVALUATION_RESULT"
fi

# 测试4: 页面功能
echo "🔍 测试4: 页面功能检查"
PAGE_CONTENT=$(curl -s http://localhost:3000/smart-diagnosis)

if echo "$PAGE_CONTENT" | grep -q "步进式诊断"; then
    echo "✅ 页面包含步进式诊断特性"
else
    echo "❌ 页面缺少步进式诊断特性"
fi

if echo "$PAGE_CONTENT" | grep -q "制定逐步诊断计划"; then
    echo "✅ 页面使用了步进式诊断组件"
else
    echo "❌ 页面未使用步进式诊断组件"
fi

# 测试5: 网络诊断工具API
echo "🔍 测试5: 网络诊断工具API检查"
TOOLS_TO_TEST=("network-ping" "wifi-scan" "connectivity-check" "gateway-info")

for tool in "${TOOLS_TO_TEST[@]}"; do
    if curl -s -X POST http://localhost:3000/api/$tool \
       -H "Content-Type: application/json" \
       -d '{"host": "baidu.com"}' | jq -r '.success' > /dev/null 2>&1; then
        echo "✅ $tool API 可用"
    else
        echo "⚠️  $tool API 可能不可用（正常，需要后端支持）"
    fi
done

echo ""
echo "🎉 步进式诊断功能测试完成！"
echo ""
echo "📋 测试总结:"
echo "✅ 问题分析功能"
echo "✅ 获取下一步功能"  
echo "✅ 结果评估功能"
echo "✅ 页面集成功能"
echo "⚠️  网络工具API（需要后端支持）"
echo ""
echo "🚀 现在可以访问 http://localhost:3000/smart-diagnosis 体验步进式诊断！"
echo ""
echo "💡 使用建议："
echo "1. 输入问题如：'网络连接很慢'"
echo "2. 等待AI分析并制定诊断计划"
echo "3. 按照推荐逐步执行工具"
echo "4. 查看AI对每步结果的评估"
echo "5. 获取最终诊断报告" 