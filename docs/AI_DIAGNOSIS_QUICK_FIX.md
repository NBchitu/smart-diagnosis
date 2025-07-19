# AI诊断功能错误修复指南

## 问题描述
前端AI诊断API返回错误 `"3:"An error occurred.""`

## 问题原因
环境变量未配置，导致AI客户端初始化失败。

## 解决步骤

### 1. 配置环境变量

在 `frontend` 目录下创建 `.env.local` 文件：

```bash
cd frontend
cp .env.example .env.local
```

### 2. 填写API密钥

编辑 `.env.local` 文件，选择一个AI提供商并填写相应的API密钥：

#### 选项A: OpenRouter (推荐)
```env
NEXT_PUBLIC_AI_PROVIDER=openrouter
NEXT_PUBLIC_OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
NEXT_PUBLIC_OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

#### 选项B: OpenAI
```env
NEXT_PUBLIC_AI_PROVIDER=openai
NEXT_PUBLIC_OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_OPENAI_BASE_URL=https://api.openai.com/v1
NEXT_PUBLIC_OPENAI_MODEL=gpt-4
```

#### 选项C: Anthropic
```env
NEXT_PUBLIC_AI_PROVIDER=anthropic
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
NEXT_PUBLIC_ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 3. 获取API密钥

#### OpenRouter (推荐)
1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册账号并登录
3. 点击 "API Keys" 创建新的API密钥
4. 复制密钥到 `.env.local` 文件

#### OpenAI
1. 访问 [OpenAI API](https://platform.openai.com/)
2. 登录并进入API Keys页面
3. 创建新的API密钥
4. 复制密钥到 `.env.local` 文件

### 4. 重启开发服务器

```bash
# 在frontend目录下
yarn dev
# 或
npm run dev
```

### 5. 测试功能

1. 访问 http://localhost:3000/ai-diagnosis
2. 输入网络问题描述
3. 确认AI能正常回复

## 降级方案

如果暂时无法配置AI API，系统会自动使用内置的基础诊断模式，可以提供基本的网络问题解决建议。

## 常见问题

### Q1: 仍然出现错误怎么办？
- 检查API密钥是否正确
- 确认环境变量名称正确
- 重启开发服务器

### Q2: OpenRouter与其他AI服务的区别？
- OpenRouter：聚合多个AI模型，性价比高
- OpenAI：官方API，稳定性好
- Anthropic：Claude模型，对话质量高

### Q3: 如何切换AI提供商？
修改 `.env.local` 中的 `NEXT_PUBLIC_AI_PROVIDER` 值即可。

## 技术实现

修复包含以下改进：
1. **错误处理增强**：添加了AI客户端创建失败的处理
2. **降级方案**：AI不可用时提供基础诊断功能
3. **流式响应修复**：使用正确的ai/react流式格式
4. **类型安全**：修复TypeScript类型错误

## 下一步

配置完成后，您可以：
1. 测试AI诊断功能
2. 体验智能网络问题分析
3. 查看完整的配置指南：`docs/OPENROUTER_CONFIGURATION_GUIDE.md` 