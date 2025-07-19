# 网络抓包与AI分析自动化系统

## 📋 项目概述

这是一个基于树莓派5的智能网络诊断系统，能够根据用户反馈的网络问题自动选择抓包策略，精准采集网络数据，并通过AI大模型进行智能分析和诊断。

## 🚀 主要功能

### 1. 智能抓包控制
- **问题类型识别**: 支持网速慢、DNS解析慢、频繁掉线、局域网互通异常、视频卡顿等常见问题
- **自动过滤策略**: 根据问题类型自动生成最优的tcpdump过滤表达式
- **灵活配置**: 支持自定义抓包时长、网络接口、目标IP/端口等参数

### 2. 数据包预处理
- **结构化摘要**: 提取关键网络统计信息，包括协议分布、流量统计、异常事件等
- **问题特定分析**: 针对不同问题类型进行专门的数据分析
  - DNS问题: 查询响应时间、失败率、慢查询统计
  - 性能问题: TCP重传、连接延迟、带宽使用
  - 连接问题: 连接成功率、重置统计、超时分析
  - 局域网问题: ARP解析、ICMP响应、设备可达性
  - 视频问题: UDP丢包、网络抖动、包大小分析

### 3. AI智能诊断
- **多模型支持**: 兼容OpenRouter、OpenAI、Anthropic等AI服务
- **专业prompt**: 针对不同网络问题生成专业的分析提示词
- **结构化输出**: 提供诊断结论、严重程度、根本原因、解决建议等

### 4. 用户友好界面
- **步骤化流程**: 清晰的5步诊断流程（选择问题→抓包→预处理→AI分析→结果展示）
- **实时进度**: 显示任务进度和状态更新
- **结果可视化**: 美观的AI分析结果和抓包统计展示

## 🛠️ 技术架构

### 后端 (FastAPI + Python)
```
backend/
├── app/
│   ├── api/
│   │   └── capture.py          # 抓包API接口
│   ├── services/
│   │   └── ai_analysis_service.py  # AI分析服务
│   └── config/
│       └── ai_config.py        # AI配置管理
```

### 前端 (Next.js + React)
```
frontend/
└── app/
    ├── api/capture/            # API代理
    └── network-capture-ai-test/ # 用户界面
```

## 📦 安装和配置

### 1. 系统要求
- Python 3.8+
- Node.js 16+
- tcpdump (Linux网络抓包工具)
- sudo权限 (用于网络抓包)

### 2. 安装依赖

#### 后端依赖
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install  # 或 yarn install
```

### 3. AI配置
设置环境变量或创建`.env`文件：

```bash
# OpenRouter (推荐)
export OPENROUTER_API_KEY="your-openrouter-key"
export OPENROUTER_MODEL="anthropic/claude-3-sonnet"

# 或者 OpenAI
export OPENAI_API_KEY="your-openai-key"
export OPENAI_MODEL="gpt-4o-mini"

# 或者 Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"
export ANTHROPIC_MODEL="claude-3-sonnet-20240229"
```

### 4. 系统配置
```bash
# 安装tcpdump (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install tcpdump

# 配置sudo权限 (可选，避免每次输入密码)
sudo visudo
# 添加: your-username ALL=(ALL) NOPASSWD: /usr/bin/tcpdump
```

## 🚀 使用方法

### 1. 启动服务

#### 方法一: 使用测试脚本 (推荐)
```bash
./scripts/test-network-capture-ai.sh
```

#### 方法二: 手动启动
```bash
# 启动后端
cd backend
source venv/bin/activate
python start_dev.py

# 启动前端 (新终端)
cd frontend
npm run dev
```

### 2. 访问界面
打开浏览器访问: `http://localhost:3000/network-capture-ai-test`

### 3. 使用流程
1. **选择问题类型**: 从预设问题中选择或自定义描述
2. **自动抓包**: 系统根据问题类型自动执行网络抓包
3. **数据预处理**: 智能提取和分析关键网络信息
4. **AI分析**: 调用大模型进行专业诊断
5. **查看结果**: 获得详细的诊断报告和解决建议

## 🧪 测试和演示

### 1. 运行演示脚本
```bash
cd backend
source venv/bin/activate
python demo_network_capture.py
```

### 2. 运行集成测试
```bash
cd backend
source venv/bin/activate
python test_network_capture_ai.py
```

### 3. 使用测试脚本
```bash
./scripts/test-network-capture-ai.sh
```

## 📊 支持的问题类型

| 问题类型 | 抓包策略 | 分析重点 | 应用场景 |
|---------|---------|---------|---------|
| 网速慢 | TCP/UDP 80/443端口 | 重传率、延迟、带宽 | 网页加载慢、下载慢 |
| DNS解析慢 | 53端口 | 查询响应时间、失败率 | 域名解析超时 |
| 频繁掉线 | TCP连接状态 | 连接重置、成功率 | 网络连接不稳定 |
| 局域网异常 | ARP、ICMP | 设备可达性、响应率 | 局域网设备无法访问 |
| 视频卡顿 | UDP流媒体端口 | 丢包率、抖动、延迟 | 视频播放卡顿 |

## 🔧 配置选项

### 抓包配置
```python
{
    "issue_type": "dns",           # 问题类型
    "duration": 10,                # 抓包时长(秒)
    "interface": "eth0",           # 网络接口
    "target_ip": "8.8.8.8",       # 目标IP(可选)
    "target_port": 53,             # 目标端口(可选)
    "custom_filter": "",           # 自定义过滤器(可选)
    "user_description": "DNS慢",   # 用户描述
    "enable_ai_analysis": true     # 启用AI分析
}
```

### AI配置
```python
{
    "provider": "openrouter",      # AI提供商
    "model": "claude-3-sonnet",    # 模型名称
    "max_tokens": 4000,            # 最大token数
    "temperature": 0.7,            # 创造性参数
    "timeout": 30                  # 超时时间(秒)
}
```

## 🐛 故障排除

### 常见问题

1. **抓包权限错误**
   ```bash
   # 解决方案: 使用sudo或配置权限
   sudo python start_dev.py
   ```

2. **AI分析失败**
   ```bash
   # 检查API密钥配置
   echo $OPENROUTER_API_KEY
   ```

3. **网络接口不存在**
   ```bash
   # 查看可用接口
   ip link show
   ```

4. **依赖安装失败**
   ```bash
   # 更新包管理器
   sudo apt-get update
   pip install --upgrade pip
   ```

### 日志查看
```bash
# 后端日志
tail -f backend/logs/app.log

# 前端日志
# 查看浏览器控制台
```

## 🔮 扩展功能

### 1. 添加新的问题类型
在`capture.py`中的`get_filter_by_issue`函数添加新的过滤规则

### 2. 自定义AI分析模板
在`ai_analysis_service.py`中修改prompt模板

### 3. 集成新的AI模型
在`ai_config.py`中添加新的提供商配置

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如有问题，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本系统需要适当的网络权限和AI API配置才能正常工作。在生产环境中使用前，请确保已正确配置所有依赖项。
