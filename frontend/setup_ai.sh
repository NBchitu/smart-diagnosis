#!/bin/bash

echo "🤖 AI诊断功能快速设置"
echo "======================="

# 检查是否在frontend目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在frontend目录下运行此脚本"
    exit 1
fi

# 检查.env.example是否存在
if [ ! -f ".env.example" ]; then
    echo "📝 创建环境变量示例文件..."
    cat > .env.example << 'ENVEOF'
# AI诊断服务配置示例
# 复制此文件为 .env.local 并填写您的API密钥

# 选择AI提供商: openrouter, openai, anthropic
NEXT_PUBLIC_AI_PROVIDER=openrouter

# OpenRouter配置 (推荐使用)
NEXT_PUBLIC_OPENROUTER_API_KEY=your_openrouter_api_key_here
NEXT_PUBLIC_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
NEXT_PUBLIC_OPENROUTER_MODEL=anthropic/claude-3-sonnet

# OpenAI配置 (可选)
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key_here
NEXT_PUBLIC_OPENAI_BASE_URL=https://api.openai.com/v1
NEXT_PUBLIC_OPENAI_MODEL=gpt-4

# Anthropic配置 (可选)
NEXT_PUBLIC_ANTHROPIC_API_KEY=your_anthropic_api_key_here
NEXT_PUBLIC_ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
NEXT_PUBLIC_ANTHROPIC_MODEL=claude-3-sonnet-20240229
ENVEOF
fi

# 复制.env.example到.env.local
if [ ! -f ".env.local" ]; then
    echo "📋 创建环境变量配置文件..."
    cp .env.example .env.local
    echo "✅ 已创建 .env.local 文件"
else
    echo "⚠️  .env.local 文件已存在，跳过复制"
fi

echo ""
echo "�� 后续步骤："
echo "1. 编辑 .env.local 文件，填写您的API密钥"
echo "2. 推荐使用 OpenRouter (访问 https://openrouter.ai/ 获取API密钥)"
echo "3. 重启开发服务器: yarn dev"
echo "4. 访问 http://localhost:3000/ai-diagnosis 测试功能"
echo ""
echo "📚 详细文档："
echo "- docs/AI_DIAGNOSIS_QUICK_FIX.md - 快速修复指南"
echo "- docs/OPENROUTER_CONFIGURATION_GUIDE.md - 完整配置指南"
echo ""
echo "🎉 设置完成！"
