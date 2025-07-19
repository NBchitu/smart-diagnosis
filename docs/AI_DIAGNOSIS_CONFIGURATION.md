# AI诊断服务配置指南

## 概述
AI诊断服务支持OpenRouter和OpenAI两种AI提供商，通过环境变量进行配置。

## 环境变量配置

### OpenRouter配置（推荐）
在 `frontend/.env.local` 文件中添加：

```bash
# AI诊断服务配置
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

### OpenAI配置（可选）
```bash
# AI诊断服务配置
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## 获取API密钥

### OpenRouter API密钥
1. 访问 [OpenRouter官网](https://openrouter.ai/)
2. 注册并登录账户
3. 进入API密钥页面
4. 创建新的API密钥
5. 将密钥复制到 `OPENROUTER_API_KEY` 环境变量

### OpenAI API密钥
1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册并登录账户
3. 进入API密钥页面
4. 创建新的API密钥
5. 将密钥复制到 `OPENAI_API_KEY` 环境变量

## 支持的模型

### OpenRouter模型
- `anthropic/claude-3-sonnet` (推荐)
- `anthropic/claude-3-haiku`
- `openai/gpt-4o-mini`
- `openai/gpt-4o`

### OpenAI模型
- `gpt-4o-mini` (推荐)
- `gpt-4o`
- `gpt-3.5-turbo`

## 配置验证

启动开发服务器后，AI诊断服务会自动检测配置：

```bash
# 成功配置示例
✅ 使用OpenRouter AI模型: anthropic/claude-3-sonnet

# 配置缺失示例
⚠️ 未检测到有效的AI API密钥，使用模拟AI客户端进行工具调用演示
```

## 降级机制

当AI配置不可用时，系统会自动降级到模拟模式：
- 仍可执行网络诊断工具（如ping测试）
- 提供基础的故障排除建议
- 保证系统基本功能可用

## 故障排除

### 常见问题

1. **API密钥无效**
   - 检查密钥是否正确复制
   - 确认密钥是否有效且未过期
   - 验证账户是否有足够的额度

2. **模型不支持**
   - 确认使用了支持的模型名称
   - 检查账户是否有权限使用该模型

3. **网络连接问题**
   - 检查网络连接是否正常
   - 确认防火墙设置不会阻止API调用

### 调试方法

1. 查看浏览器控制台的网络请求
2. 检查服务器日志输出
3. 使用 `/api/test-ai` 端点测试AI配置

## 使用建议

1. **开发环境**: 使用OpenRouter的免费额度进行开发测试
2. **生产环境**: 根据使用量选择合适的AI提供商
3. **成本控制**: 监控API使用量，设置合理的使用限制

## 更新说明

- 支持实时ping工具调用
- 智能降级机制确保服务可用性
- 灵活的AI提供商切换
- 详细的配置验证和错误提示 