# AI诊断系统配置指南

## 概述
本系统支持真实的AI智能诊断功能，可以使用OpenRouter或OpenAI API进行智能网络故障排查。

## 快速配置步骤

### 方案1：使用OpenRouter（推荐）
OpenRouter提供多种AI模型选择，包括Claude、GPT等，价格更优惠。

1. **注册OpenRouter账户**
   - 访问 https://openrouter.ai/
   - 注册并获取API密钥

2. **配置环境变量**
   ```bash
   # 在backend目录下创建.env文件
   cd backend
   cp .env.example .env
   
   # 编辑.env文件，添加以下内容：
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=anthropic/claude-3-sonnet
   AI_PROVIDER=openrouter
   ```

3. **推荐模型选择**
   - `anthropic/claude-3-sonnet` - 高质量分析（推荐）
   - `openai/gpt-4o-mini` - 快速响应
   - `anthropic/claude-3-haiku` - 经济实惠

### 方案2：使用OpenAI
1. **获取OpenAI API密钥**
   - 访问 https://platform.openai.com/
   - 注册并获取API密钥

2. **配置环境变量**
   ```bash
   # 编辑.env文件
   OPENAI_API_KEY=sk-your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   AI_PROVIDER=openai
   ```

## 启动系统

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 验证配置

1. **检查API配置**
   - 启动后端服务
   - 查看控制台日志，确认显示"使用真实AI模型"而非"模拟AI客户端"

2. **测试AI诊断**
   - 访问 http://localhost:3000/ai-diagnosis
   - 输入网络问题描述，如："我无法连接到百度网站，请帮我诊断"
   - 系统应该智能调用ping工具并提供专业分析

## 功能特性

### 智能工具调用
- AI会根据问题描述自动判断需要使用哪些诊断工具
- 支持ping测试、速度测试、WiFi扫描等多种工具
- 提供专业的故障分析和解决建议

### 实时流式响应
- 支持实时显示AI分析过程
- 工具调用结果即时反馈
- 流畅的对话式交互体验

## 故障排查

### 常见问题
1. **"使用模拟AI客户端"提示**
   - 检查.env文件中的API密钥是否正确配置
   - 确认API密钥格式正确（OpenRouter密钥不以sk-开头）

2. **API调用失败**
   - 检查网络连接
   - 验证API密钥是否有效
   - 确认账户余额充足

3. **前端无法连接后端**
   - 确认后端服务在8000端口运行
   - 检查CORS配置

### 支持的诊断工具
- **ping_test** - 网络连通性检测
- **speed_test** - 网络速度测试
- **wifi_scan** - WiFi信号扫描
- **signal_analysis** - 信号质量分析
- **trace_route** - 路由追踪
- **analyze_network_problem** - 智能问题分析
- **generate_diagnostic_sequence** - 生成诊断序列
- **evaluate_diagnostic_results** - 评估诊断结果

## 技术架构
- **前端**: Next.js 15 + AI SDK
- **后端**: FastAPI + MCP架构
- **AI集成**: OpenRouter/OpenAI API
- **网络工具**: 系统原生命令 + Python库

## 注意事项
- 确保系统有ping、traceroute等网络工具
- 生产环境建议使用环境变量管理API密钥
- 定期检查API使用量和账户余额