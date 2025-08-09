# 网络诊断工具安装指南

本文档介绍如何在 macOS 和树莓派 5 系统上安装网络诊断工具的依赖。

## 🚀 快速安装

### 自动安装脚本

运行自动安装脚本（推荐）：

```bash
cd backend
python3 scripts/install_dependencies.py
```

### 手动安装

如果自动安装失败，可以按照以下步骤手动安装。

## 🍎 macOS 系统

### 1. 安装 Homebrew（如果未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装系统工具

```bash
# 网络测速工具
brew install speedtest-cli

# DNS 查询工具
brew install bind

# 路由追踪工具（通常已预装）
brew install traceroute

# SSL 工具（通常已预装）
brew install openssl

# 网络扫描工具（可选）
brew install nmap
```

### 3. 安装 Python 依赖

```bash
pip3 install speedtest-cli cryptography requests
```

## 🐧 树莓派 5 (Linux) 系统

### 1. 更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装系统工具

```bash
# 基础网络工具
sudo apt install -y dnsutils traceroute openssl net-tools iputils-ping curl wget

# Python 包管理器
sudo apt install -y python3-pip

# 网络扫描工具（可选）
sudo apt install -y nmap
```

### 3. 安装 Python 依赖

```bash
pip3 install speedtest-cli cryptography requests
```

## 🔍 验证安装

运行以下命令验证工具是否正确安装：

```bash
# 网络测速
speedtest-cli --version

# DNS 查询
dig google.com

# 路由追踪
traceroute google.com

# SSL 检查
openssl version

# Ping 测试
ping -c 3 google.com
```

## 🛠️ 工具说明

### 必需工具

| 工具 | 用途 | macOS | Linux | 备用方案 |
|------|------|-------|-------|----------|
| `speedtest-cli` | 网络测速 | ✅ | ✅ | 简单HTTP下载测试 |
| `dig` | DNS查询 | ✅ | ✅ | `nslookup` 或 Python socket |
| `traceroute` | 路由追踪 | ✅ | ✅ | 简单连接测试 |
| `openssl` | SSL检查 | ✅ | ✅ | Python ssl 模块 |
| `ping` | 网络延迟 | ✅ | ✅ | Python socket |

### 可选工具

| 工具 | 用途 | 说明 |
|------|------|------|
| `nmap` | 高级端口扫描 | 提供更详细的扫描功能 |
| `curl` | HTTP测试 | 用于连通性检查 |
| `wget` | 文件下载 | 备用下载工具 |

## 🔧 故障排除

### 常见问题

#### 1. speedtest-cli 安装失败

**解决方案**：
```bash
# 尝试使用 pip 直接安装
pip3 install --user speedtest-cli

# 或者使用系统包管理器
# macOS:
brew install speedtest-cli

# Linux:
sudo apt install speedtest-cli
```

#### 2. dig 命令不存在

**解决方案**：
```bash
# macOS:
brew install bind

# Linux:
sudo apt install dnsutils
```

#### 3. 权限问题

**解决方案**：
```bash
# 使用 --user 标志安装 Python 包
pip3 install --user speedtest-cli

# 或者使用 sudo（不推荐）
sudo pip3 install speedtest-cli
```

#### 4. 网络连接问题

如果安装过程中遇到网络问题：

1. 检查网络连接
2. 尝试使用代理
3. 使用国内镜像源

```bash
# 使用清华大学镜像
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ speedtest-cli
```

## 📝 备用方案

即使某些工具安装失败，网络诊断系统仍然可以工作：

- **网络测速**: 使用简单的HTTP下载测试
- **DNS测试**: 使用Python内置的socket模块
- **路由追踪**: 使用简单的多跳连接测试
- **SSL检查**: 使用Python ssl模块的基础功能
- **端口扫描**: 使用Python socket进行基础扫描

## 🎯 性能优化建议

### macOS 系统

1. 使用 Homebrew 安装工具获得最佳性能
2. 确保 Xcode Command Line Tools 已安装
3. 定期更新工具版本

### 树莓派 5 系统

1. 使用 apt 包管理器安装系统工具
2. 考虑使用轻量级替代方案
3. 监控系统资源使用情况

## 📞 技术支持

如果遇到安装问题：

1. 查看错误日志
2. 检查系统兼容性
3. 尝试手动安装单个工具
4. 使用备用安装方法

## 🔄 更新说明

定期更新工具以获得最新功能和安全修复：

```bash
# 更新 Homebrew 工具 (macOS)
brew update && brew upgrade

# 更新 apt 包 (Linux)
sudo apt update && sudo apt upgrade

# 更新 Python 包
pip3 install --upgrade speedtest-cli cryptography requests
```
