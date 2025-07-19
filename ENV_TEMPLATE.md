# 环境变量配置模板

## 🔧 环境变量设置指南

### 1. 前端环境变量 (`frontend/.env.local`)

复制以下内容到 `frontend/.env.local` 文件：

```bash
# OpenRouter配置（推荐）
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# AI提供商选择 (openrouter/openai/anthropic)
AI_PROVIDER=openrouter

# 备用OpenAI配置
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 后端API地址
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 2. 后端环境变量 (`backend/.env`)

复制以下内容到 `backend/.env` 文件：

```bash
# OpenRouter配置（推荐）
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# AI提供商选择
AI_PROVIDER=openrouter

# 备用配置
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# 调试和开发
DEBUG=true
LOG_LEVEL=INFO

# 数据库（如果需要）
DATABASE_URL=sqlite:///./app.db
```

## 📝 配置说明

### OpenRouter模型推荐

| 用途 | 模型名称 | 特点 |
|------|----------|------|
| **日常使用** | `anthropic/claude-3-sonnet` | 平衡性能和成本 |
| **高性能** | `anthropic/claude-3.5-sonnet` | 最新最强 |
| **经济型** | `anthropic/claude-3-haiku` | 快速便宜 |
| **OpenAI** | `openai/gpt-4o` | GPT-4最新版 |
| **轻量级** | `openai/gpt-4o-mini` | 成本效益高 |

### 获取API密钥

1. **OpenRouter** (推荐)：
   - 访问：https://openrouter.ai/
   - 注册并前往：https://openrouter.ai/keys
   - 创建新密钥（格式：`sk-or-v1-...`）

2. **OpenAI**：
   - 访问：https://platform.openai.com/
   - 前往：https://platform.openai.com/api-keys
   - 创建新密钥（格式：`sk-...`）

3. **Anthropic**：
   - 访问：https://console.anthropic.com/
   - 前往API密钥页面
   - 创建新密钥（格式：`sk-ant-...`）

## ⚠️ 重要提醒

1. **不要提交密钥到Git**：
   - 确保 `.env.local` 和 `.env` 在 `.gitignore` 中
   - 定期轮换API密钥

2. **成本控制**：
   - 开发时使用便宜的模型
   - 设置API使用限制
   - 监控费用

3. **配置验证**：
   ```bash
   # 测试前端配置
   cd frontend && yarn dev
   
   # 测试后端配置
   cd backend && python start_dev.py
   ```

---

配置完成后，重启服务即可使用OpenRouter强大的AI功能！🚀 