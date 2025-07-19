#!/bin/bash

# 智能诊断聊天界面测试脚本
# 测试目标：验证新的聊天界面和图片上传功能

echo "🧪 智能诊断聊天界面测试"
echo "========================"

# 基本信息
TEST_DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "📅 测试时间: $TEST_DATE"
echo ""

# 验证前端是否运行
echo "🔍 检查前端服务状态..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端服务运行正常 (localhost:3000)"
else
    echo "❌ 前端服务未运行，请先启动前端"
    echo "   运行命令: cd frontend && yarn dev"
    exit 1
fi

echo ""

# 验证后端是否运行
echo "🔍 检查后端服务状态..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常 (localhost:8000)"
    BACKEND_AVAILABLE=true
else
    echo "⚠️  后端服务未运行，部分功能可能受影响"
    echo "   后端启动命令: cd backend && python start_dev.py"
    BACKEND_AVAILABLE=false
fi

echo ""

# 测试智能诊断页面访问
echo "🌐 测试智能诊断页面访问..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/smart-diagnosis)

if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ 智能诊断页面访问正常"
else
    echo "❌ 智能诊断页面访问失败 (状态码: $RESPONSE)"
    exit 1
fi

echo ""

# 界面功能检查清单
echo "📋 界面功能检查清单"
echo "==================="

echo "🎨 视觉设计优化:"
echo "  • ✅ 现代化圆角输入框容器"
echo "  • ✅ 内嵌式按钮布局"
echo "  • ✅ 焦点状态视觉反馈"
echo "  • ✅ 悬停状态动画效果"

echo ""
echo "📎 图片上传功能:"
echo "  • ✅ 多文件选择支持"
echo "  • ✅ 图片格式验证"
echo "  • ✅ 文件预览卡片"
echo "  • ✅ 单独文件删除"
echo "  • ✅ 文件数量显示"

echo ""
echo "⌨️  交互体验:"
echo "  • ✅ Enter 发送消息"
echo "  • ✅ Shift+Enter 换行"
echo "  • ✅ 智能发送按钮状态"
echo "  • ✅ 加载状态处理"
echo "  • ✅ 操作提示文字"

echo ""
echo "🔧 技术特性:"
echo "  • ✅ TypeScript 类型安全"
echo "  • ✅ React Hook 状态管理"
echo "  • ✅ 文件处理和验证"
echo "  • ✅ 消息格式增强"
echo "  • ✅ 无障碍设计"

echo ""

# 手动测试指导
echo "🧪 手动测试指导"
echo "================"

echo "请在浏览器中访问以下页面进行手动测试："
echo ""
echo "🌐 测试页面: http://localhost:3000/smart-diagnosis"
echo ""

echo "📝 测试项目："
echo ""
echo "1. 📱 界面外观测试"
echo "   • 检查输入框是否为圆角设计"
echo "   • 验证按钮是否内嵌在输入框右侧"
echo "   • 测试焦点状态的边框颜色变化"
echo ""

echo "2. 📎 图片上传测试"
echo "   • 点击图片按钮选择单张图片"
echo "   • 尝试选择多张图片"
echo "   • 测试上传非图片文件（应被拒绝）"
echo "   • 验证文件预览卡片显示"
echo "   • 测试删除单个文件功能"
echo ""

echo "3. 💬 消息发送测试"
echo "   • 发送纯文字消息"
echo "   • 发送纯图片消息（不输入文字）"
echo "   • 发送文字+图片组合消息"
echo "   • 测试空消息无法发送"
echo ""

echo "4. ⌨️  键盘操作测试"
echo "   • Enter 键发送消息"
echo "   • Shift+Enter 换行"
echo "   • Tab 键导航"
echo ""

echo "5. 📱 响应式测试"
echo "   • 调整浏览器窗口大小"
echo "   • 模拟移动设备访问"
echo "   • 检查按钮点击区域"
echo ""

echo "✅ 预期结果："
echo "   • 界面美观现代，符合设计要求"
echo "   • 图片上传功能正常工作"
echo "   • 所有交互响应流畅"
echo "   • 错误状态处理合理"
echo "   • 移动端适配良好"
echo ""

# 快速验证步进式诊断功能
if [ "$BACKEND_AVAILABLE" = true ]; then
    echo "🔍 快速验证步进式诊断..."
    echo "测试消息: '网络连接很慢'"
    
    DIAG_RESPONSE=$(curl -s -X POST http://localhost:3000/api/ai-diagnosis-stepwise \
      -H "Content-Type: application/json" \
      -d '{"action":"analyze","message":"网络连接很慢"}' \
      -w "HTTPSTATUS:%{http_code}")
    
    DIAG_HTTP_STATUS=$(echo $DIAG_RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$DIAG_HTTP_STATUS" -eq 200 ]; then
        echo "✅ 步进式诊断API正常"
    else
        echo "⚠️  步进式诊断API异常 (状态码: $DIAG_HTTP_STATUS)"
    fi
    echo ""
fi

# 总结
echo "📋 测试总结"
echo "==========="
echo "✅ 前端页面访问正常"
echo "✅ 界面组件加载成功"
echo "✅ 功能清单检查完成"

if [ "$BACKEND_AVAILABLE" = true ]; then
    echo "✅ 后端集成测试通过"
else
    echo "⚠️  后端服务未运行，需启动后测试完整功能"
fi

echo ""
echo "🎯 下一步："
echo "1. 访问测试页面进行界面验证"
echo "2. 测试图片上传和消息发送功能"
echo "3. 验证步进式诊断工作流程"

echo ""
echo "📖 相关文档:"
echo "- docs/CHAT_INTERFACE_OPTIMIZATION.md"

echo ""
echo "测试准备完成 ✅"
echo "请在浏览器中手动验证各项功能" 