# 🌐 树莓派网络检测工具

基于树莓派5的专业宽带网络检测和故障诊断工具，专为宽带运维人员（装维）设计。

## 📋 项目概述

这是一个完整的网络诊断解决方案，包含：
- 📱 移动端友好的Web界面
- 🔧 专业的网络检测功能  
- 🤖 AI智能故障分析
- ⚙️ 路由器自动配置
- 📊 实时数据可视化

### 使用场景
1. 手机连接树莓派热点
2. 访问Web界面进行网络检测
3. 查看实时分析结果和AI建议
4. 自动优化网络配置

## 🚀 快速开始

### 🔥 智能诊断助手 2.0 (推荐)
```bash
# 一键启动完整系统
./scripts/start-smart-diagnosis.sh

# 或手动启动
cd frontend && yarn dev &
cd backend && python start_dev.py &
```
访问: **http://localhost:3000/smart-diagnosis**

### 传统开发模式
```bash
# 前端开发
cd frontend
yarn install
yarn dev

# 后端开发  
cd backend
pip install -r requirements.txt
python start_dev.py
```
- 前端: http://localhost:3000
- API文档: http://localhost:8000/docs

## 🏗️ 技术架构

### 前端技术栈
- **框架**: Next.js 14 + React 18 + TypeScript
- **UI库**: shadcn/ui + Tailwind CSS
- **状态管理**: TanStack Query + Zustand
- **图表**: Recharts
- **实时通信**: WebSocket

### 后端技术栈
- **框架**: FastAPI + Python 3.9+
- **异步**: uvicorn + asyncio
- **网络检测**: speedtest-cli + ping3 + scapy
- **系统监控**: psutil
- **AI分析**: OpenAI + Anthropic (MCP)

## 📁 项目结构

```
device-panel/
├── frontend/                   # Next.js前端应用
│   ├── app/                   # App Router页面
│   │   ├── components/            # React组件
│   │   │   ├── ui/               # shadcn/ui组件
│   │   │   ├── network/          # 网络检测组件
│   │   │   ├── wifi/             # WiFi相关组件
│   │   │   └── charts/           # 图表组件
│   │   ├── hooks/                # 自定义Hook
│   │   └── lib/                  # 工具函数
│   ├── backend/                   # FastAPI后端服务
│   │   ├── app/
│   │   │   ├── api/              # API路由
│   │   │   ├── core/             # 核心功能
│   │   │   ├── services/         # 业务逻辑
│   │   │   └── utils/            # 工具函数
│   │   └── requirements.txt      # Python依赖
│   ├── scripts/                   # 部署脚本
│   └── config/                    # 配置文件
└── docs/                      # 文档
```

## 🔧 核心功能

### 🌟 智能诊断助手 2.0 (最新)
- ✅ **AI智能故障分析** - 基于自然语言描述问题
- ✅ **智能工具推荐** - AI自动推荐最合适的诊断工具
- ✅ **一键工具执行** - 卡片式界面，点击即可执行
- ✅ **可视化结果展示** - 专业的结果卡片和图表
- ✅ **稳定API调用** - 工具执行基于HTTP API，更加稳定

### 1. 网络检测
- ✅ 带宽测试 (上传/下载速度)
- ✅ 延迟和丢包检测 (Ping)
- ✅ 路由跟踪
- ✅ 连通性全面检查

### 2. WiFi分析
- ✅ WiFi信号扫描
- ✅ 信号强度监控
- ⏳ 信道干扰分析
- ⏳ 覆盖热图

### 3. 路由器管理
- ✅ 网关信息获取
- ⏳ 自动检测路由器型号
- ⏳ 智能登录路由器
- ⏳ 配置优化建议

### 4. 数据包分析
- ✅ 实时数据包捕获
- ✅ AI智能分析
- ✅ 网络流量监控
- ✅ 协议分析

### 5. 系统监控
- ✅ 系统资源监控
- ✅ 网络接口状态
- ✅ 温度监控（树莓派）
- ⏳ 历史数据记录

## 💡 智能诊断使用指南

### 1. 问题描述
用自然语言描述网络问题，例如：
- "网络连接很慢，打开网页要等很久"
- "WiFi信号不稳定，时强时弱"
- "无法访问某些特定网站"
- "网络经常断线，需要重新连接"

### 2. AI智能分析
系统将自动：
- 🧠 分析故障原因和类型
- 🎯 评估问题紧急程度
- 💡 推荐最合适的诊断工具

### 3. 工具执行
在推荐的工具卡片中：
- 📋 查看工具说明和预估时间
- ⚙️ 配置高级参数（可选）
- ▶️ 点击"立即执行"运行诊断

### 4. 结果查看
- 📊 可视化结果卡片
- 📈 实时状态更新
- 🔍 详细数据分析

## 📱 移动端优化

- 📱 响应式设计，完美适配手机
- 👆 触摸友好的大按钮
- 📊 实时图表展示
- 🔄 WebSocket实时更新
- 💾 PWA支持，类原生体验

## 🛠️ 开发进度

### ✅ Phase 1: 基础框架 (已完成)
- [x] 项目结构搭建
- [x] 前端框架 (Next.js + shadcn/ui)
- [x] 后端API框架 (FastAPI)
- [x] 基础UI组件
- [x] WebSocket通信

### 🚧 Phase 2: 核心功能 (进行中)
- [x] 网络状态检测API
- [x] 带宽测试服务
- [x] 延迟测试服务
- [ ] WiFi扫描功能
- [ ] 前后端集成

### ⏳ Phase 3: 高级功能 (计划中)
- [ ] 网络抓包分析
- [ ] 路由器自动配置
- [ ] AI分析集成
- [ ] MCP客户端

### ⏳ Phase 4: 部署优化 (计划中)
- [ ] 树莓派热点配置
- [ ] 一键安装脚本
- [ ] 系统集成测试
- [ ] 用户文档

## 🚀 部署指南

### 开发环境
1. **前端**: `cd frontend && npm run dev`
2. **后端**: `cd backend && python start_dev.py`

### 生产环境 (树莓派)
```bash
# 下载并运行安装脚本
curl -sSL https://raw.githubusercontent.com/your-repo/device-panel/main/scripts/install.sh | bash

# 手动安装
git clone https://github.com/your-repo/device-panel.git
cd device-panel
sudo bash scripts/install.sh
```

## 📚 API 文档

后端API提供RESTful接口和WebSocket实时通信：

- **网络检测**: `/api/network/*`
- **WiFi管理**: `/api/wifi/*`
- **路由器配置**: `/api/router/*`
- **AI分析**: `/api/ai/*`
- **系统信息**: `/api/system/*`
- **WebSocket**: `/ws/{endpoint}`

详细API文档: http://localhost:8000/docs

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

- 📧 Email: support@example.com
- 💬 微信群: [二维码]
- 📖 文档: [详细文档链接]
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/device-panel/issues)

---

**专为运维人员设计的网络诊断利器** ��️

*最后更新: 2024年12月* # smart-diagnosis
