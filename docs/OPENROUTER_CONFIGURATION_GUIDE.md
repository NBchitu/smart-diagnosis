# OpenRouter和AI服务配置指南

## 🚀 OpenRouter简介

OpenRouter是一个AI模型聚合平台，提供统一的API接口来访问多种大型语言模型，包括Claude、GPT、Gemini等。相比直接使用各家API，OpenRouter提供：

- **统一接口**：一个API访问多个模型
- **成本优化**：比官方API更便宜的定价
- **灵活切换**：可以轻松切换不同模型
- **无需多个账户**：只需一个OpenRouter账户

## 📋 配置步骤

### 1. 获取OpenRouter API密钥

1. 访问 [OpenRouter官网](https://openrouter.ai/)
2. 注册账户并登录
3. 前往 [API密钥页面](https://openrouter.ai/keys)
4. 创建新的API密钥
5. 复制API密钥（格式如：`sk-or-v1-...`）

### 2. 前端配置

创建前端环境变量文件 `frontend/.env.local`：

```bash
# OpenRouter 配置（推荐）
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# 选择AI提供商（openrouter、openai、anthropic）
AI_PROVIDER=openrouter

# 后端API地址
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. 后端配置

创建后端环境变量文件 `backend/.env`：

```bash
# OpenRouter 配置
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# 选择AI提供商
AI_PROVIDER=openrouter

# 备用配置
OPENAI_API_KEY=your-openai-key-if-needed
ANTHROPIC_API_KEY=your-anthropic-key-if-needed

# 调试模式
DEBUG=true
```

### 4. 推荐的OpenRouter模型

根据不同需求选择合适的模型：

#### 高性能模型（推荐）
```bash
# Claude 3 Sonnet - 平衡性能和成本
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# Claude 3.5 Sonnet - 最新最强（稍贵）
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# GPT-4o - OpenAI最新模型
OPENROUTER_MODEL=openai/gpt-4o
```

#### 经济型模型
```bash
# Claude 3 Haiku - 快速便宜
OPENROUTER_MODEL=anthropic/claude-3-haiku

# GPT-4o-mini - 轻量版GPT-4
OPENROUTER_MODEL=openai/gpt-4o-mini

# Gemini Pro - Google模型
OPENROUTER_MODEL=google/gemini-pro
```

#### 专业型模型
```bash
# 代码专用
OPENROUTER_MODEL=meta-llama/codellama-34b-instruct

# 数学推理
OPENROUTER_MODEL=microsoft/wizardmath-70b
```

## 🔧 高级配置

### 环境变量详解

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `OPENROUTER_API_KEY` | OpenRouter API密钥 | 无 | `sk-or-v1-...` |
| `OPENROUTER_BASE_URL` | API基础URL | `https://openrouter.ai/api/v1` | 默认即可 |
| `OPENROUTER_MODEL` | 使用的模型 | `anthropic/claude-3-sonnet` | 见上方推荐 |
| `AI_PROVIDER` | AI提供商 | `openrouter` | `openrouter/openai/anthropic` |

### 模型参数调优

在配置文件中可以调整以下参数：

```typescript
// frontend/config/ai.config.ts
export const aiConfig = {
  // 最大令牌数
  maxTokens: 4000,
  
  // 温度（创造性）：0.0-1.0
  temperature: 0.7,
  
  // 超时时间（毫秒）
  timeout: 30000,
}
```

## 🚦 验证配置

### 1. 前端验证

启动前端开发服务器：
```bash
cd frontend
yarn dev
```

访问 http://localhost:3000/ai-diagnosis 测试AI诊断功能。

### 2. 后端验证

启动后端服务：
```bash
cd backend
python start_dev.py
```

检查启动日志中的AI配置信息。

### 3. API测试

测试AI配置接口：
```bash
curl http://localhost:8000/api/ai/status
```

期望响应：
```json
{
  "success": true,
  "provider": "openrouter",
  "model": "anthropic/claude-3-sonnet",
  "available": true
}
```

## 🔒 安全注意事项

### 1. API密钥保护
- ❌ **不要**将API密钥提交到Git仓库
- ✅ 使用环境变量文件（`.env.local`、`.env`）
- ✅ 在`.gitignore`中排除环境变量文件
- ✅ 定期轮换API密钥

### 2. 使用限制
- 设置合理的Token限制
- 监控API使用量和费用
- 在生产环境中启用速率限制

### 3. 环境隔离
```bash
# 开发环境
OPENROUTER_MODEL=anthropic/claude-3-haiku  # 便宜的模型

# 生产环境
OPENROUTER_MODEL=anthropic/claude-3-sonnet  # 性能更好
```

## 💰 成本优化

### 1. 模型选择策略
- **开发/测试**：使用便宜的模型（Haiku、GPT-4o-mini）
- **生产环境**：使用平衡的模型（Claude-3-Sonnet）
- **特殊需求**：选择专门的模型

### 2. 请求优化
- 减少不必要的API调用
- 使用合适的`max_tokens`限制
- 缓存常见的回答

### 3. 费用监控
- 在OpenRouter控制台设置费用警报
- 定期检查使用统计
- 根据需求调整模型选择

## 🛠️ 故障排除

### 常见问题

#### 1. API密钥无效
```
错误：AI配置无效: openrouter 配置不完整
```
**解决方案**：
- 检查API密钥格式（应以`sk-or-v1-`开头）
- 确认密钥在OpenRouter控制台有效
- 检查环境变量是否正确加载

#### 2. 模型不可用
```
错误：模型 anthropic/claude-3-sonnet 不可用
```
**解决方案**：
- 检查模型名称拼写
- 确认账户有权限访问该模型
- 尝试使用其他可用模型

#### 3. 网络连接问题
```
错误：连接到OpenRouter失败
```
**解决方案**：
- 检查网络连接
- 确认防火墙设置
- 尝试使用代理

#### 4. 前端配置问题
```
错误：AI配置警告: openrouter API密钥未设置
```
**解决方案**：
- 确认`.env.local`文件位于`frontend/`目录
- 重启开发服务器
- 检查环境变量名称

### 调试模式

启用详细日志：
```bash
# 前端
DEBUG=true yarn dev

# 后端
DEBUG=true python start_dev.py
```

## 📚 进阶配置

### 1. 多模型负载均衡

```typescript
// 轮询使用不同模型
const models = [
  'anthropic/claude-3-sonnet',
  'openai/gpt-4o',
  'google/gemini-pro'
];
```

### 2. 动态模型选择

```python
# 根据任务类型选择模型
def select_model(task_type: str) -> str:
    if task_type == 'code':
        return 'meta-llama/codellama-34b-instruct'
    elif task_type == 'analysis':
        return 'anthropic/claude-3-sonnet'
    else:
        return 'openai/gpt-4o-mini'
```

### 3. 企业级配置

```bash
# 高可用配置
OPENROUTER_API_KEY_PRIMARY=sk-or-v1-primary-key
OPENROUTER_API_KEY_BACKUP=sk-or-v1-backup-key

# 多区域配置
OPENROUTER_REGION=us-east-1
```

## 🔗 相关资源

- [OpenRouter官方文档](https://openrouter.ai/docs)
- [模型对比和定价](https://openrouter.ai/models)
- [API参考文档](https://openrouter.ai/docs/api-reference)
- [社区支持](https://discord.gg/openrouter)

---

配置完成后，您就可以使用OpenRouter强大的AI模型来增强网络诊断功能了！🎉 