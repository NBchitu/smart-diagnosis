# Python服务启动指南

## 🚀 快速启动

### 1. 环境准备

确保您的系统已安装：
- **Python 3.8+** (推荐 3.9 或 3.10)
- **pip** 包管理器
- **必要的系统工具**：
  - ping (网络连通性测试)
  - traceroute (路由跟踪)
  - iwlist, iwconfig (WiFi工具，Linux/树莓派)
  - tcpdump (数据包抓取，需要sudo权限)
  - speedtest-cli (带宽测试)

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动服务

#### 方式一：使用开发启动脚本（推荐）

```bash
python start_dev.py
```

#### 方式二：直接使用uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 验证服务

服务启动后，您可以访问：

- **API文档**: http://localhost:8000/docs (Swagger UI)
- **健康检查**: http://localhost:8000/health
- **WebSocket测试**: ws://localhost:8000/ws/

## 📡 服务功能

### 核心API模块

1. **网络检测** (`/api/network`)
   - 网络连通性检查
   - 带宽测试
   - 延迟测试

2. **WiFi管理** (`/api/wifi`)
   - WiFi网络扫描
   - 信号强度监控
   - 连接管理

3. **路由器信息** (`/api/router`)
   - 路由器状态
   - 网关信息
   - 端口扫描

4. **AI诊断** (`/api/ai`)
   - 智能网络诊断
   - 聊天式故障排除
   - MCP工具集成

5. **系统信息** (`/api/system`)
   - 系统状态监控
   - 硬件信息
   - 性能指标

### MCP智能诊断工具

服务集成了以下MCP诊断工具：

- **ping_server**: Ping连通性和路由跟踪
- **wifi_server**: WiFi信号分析和干扰检测
- **packet_server**: 网络抓包和流量分析
- **gateway_server**: 网关信息和性能检测
- **connectivity_server**: 综合连通性检查

## 🔧 配置说明

### 环境变量

您可以通过环境变量配置服务：

```bash
# API密钥配置
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# 服务端口(默认8000)
export PORT=8000

# 调试模式
export DEBUG=true
```

### MCP配置

MCP工具配置文件位于：`backend/config/mcp_config.json`

您可以修改工具的超时时间、传输方式等参数。

## 🚦 服务状态

### 启动成功标识

```
🚀 启动网络检测工具后端服务...
📍 API文档地址: http://localhost:8000/docs
📍 前端连接地址: http://localhost:8000
📍 WebSocket测试: ws://localhost:8000/ws/
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     正在初始化MCP管理器...
INFO:     MCP管理器初始化完成
INFO:     Application startup complete.
```

### 健康检查

```bash
curl http://localhost:8000/health
```

期望响应：
```json
{
  "status": "healthy",
  "message": "API正常运行"
}
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看8000端口占用
   lsof -i :8000
   
   # 杀死占用进程
   kill -9 <PID>
   ```

2. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 清理缓存重新安装
   pip cache purge
   pip install -r requirements.txt
   ```

3. **MCP工具初始化失败**
   - 检查系统工具是否安装（ping, traceroute等）
   - 确认sudo权限（tcpdump需要）
   - 查看日志文件：`logs/mcp_*.log`

4. **网络权限问题**（树莓派）
   ```bash
   # 添加用户到netdev组
   sudo usermod -a -G netdev $USER
   
   # 重新登录或重启
   ```

### 日志查看

服务运行时的详细日志会显示在终端中，包括：
- MCP工具初始化状态
- API请求日志
- 错误信息和警告

## 🌐 前端集成

本服务设计为与Next.js前端协同工作：

- **CORS配置**: 允许来自 localhost:3000 的请求
- **WebSocket支持**: 实时数据传输
- **RESTful API**: 标准的HTTP API接口

前端启动方式：
```bash
cd frontend
yarn dev
```

## 📱 API使用示例

### 基本网络检查

```bash
curl -X POST "http://localhost:8000/api/network/connectivity-check" \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com"}'
```

### AI智能诊断

```bash
curl -X POST "http://localhost:8000/api/ai/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "网络很慢，网页加载缓慢"}'
```

### WiFi扫描

```bash
curl -X GET "http://localhost:8000/api/wifi/scan"
```

## 🔒 安全注意事项

1. **生产环境部署**：
   - 修改默认端口
   - 配置防火墙规则
   - 使用HTTPS
   - 限制API访问权限

2. **API密钥管理**：
   - 不要在代码中硬编码密钥
   - 使用环境变量或配置文件
   - 定期轮换密钥

3. **系统权限**：
   - 网络诊断工具需要适当的系统权限
   - 使用最小权限原则
   - 定期审查权限配置

## 📖 更多文档

- [MCP集成架构](./MCP_INTEGRATION_ARCHITECTURE.md)
- [网络连通性检查功能](./NETWORK_CONNECTIVITY_CHECK_FEATURE.md)
- [WiFi实时监控功能](./WIFI_REALTIME_MONITORING_FEATURE.md)
- [AI聊天诊断功能](./AI_CHATBOT_DIAGNOSIS_FEATURE.md) 