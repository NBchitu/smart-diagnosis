#!/usr/bin/env python3
"""
网络诊断工具依赖安装脚本
支持 macOS 和树莓派 5 (Linux) 系统
"""

import subprocess
import platform
import sys
import os

def run_command(cmd, description="", timeout=60):
    """执行命令并返回结果"""
    print(f"🔧 {description}")
    print(f"   执行: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"   ✅ 成功")
            return True
        else:
            print(f"   ❌ 失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ 超时")
        return False
    except FileNotFoundError:
        print(f"   ❌ 命令未找到")
        return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def check_command_exists(cmd):
    """检查命令是否存在"""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
        return True
    except:
        try:
            subprocess.run(['which', cmd], capture_output=True, timeout=5)
            return True
        except:
            return False

def install_macos_dependencies():
    """安装 macOS 依赖"""
    print("🍎 检测到 macOS 系统")
    
    # 检查 Homebrew
    if not check_command_exists('brew'):
        print("❌ Homebrew 未安装，请先安装 Homebrew:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    dependencies = [
        ('speedtest-cli', 'brew install speedtest-cli', '网络测速工具'),
        ('dig', 'brew install bind', 'DNS查询工具'),
        ('traceroute', 'brew install traceroute', '路由追踪工具'),
        ('openssl', 'brew install openssl', 'SSL工具'),
        ('nmap', 'brew install nmap', '网络扫描工具（可选）')
    ]
    
    for cmd, install_cmd, desc in dependencies:
        if check_command_exists(cmd):
            print(f"✅ {desc} ({cmd}) 已安装")
        else:
            print(f"⚠️ {desc} ({cmd}) 未安装，尝试安装...")
            run_command(install_cmd.split(), f"安装 {desc}")
    
    # 安装 Python 依赖
    python_deps = [
        'speedtest-cli',
        'cryptography',
        'requests'
    ]
    
    for dep in python_deps:
        run_command(['pip3', 'install', dep], f"安装 Python 包: {dep}")
    
    return True

def install_linux_dependencies():
    """安装 Linux (树莓派) 依赖"""
    print("🐧 检测到 Linux 系统")
    
    # 更新包列表
    run_command(['sudo', 'apt', 'update'], "更新包列表")
    
    # 系统依赖
    system_deps = [
        'dnsutils',      # dig 命令
        'traceroute',    # traceroute 命令
        'openssl',       # SSL 工具
        'net-tools',     # 网络工具
        'iputils-ping',  # ping 命令
        'curl',          # HTTP 客户端
        'wget',          # 下载工具
        'python3-pip',   # Python 包管理器
        'nmap'           # 网络扫描工具（可选）
    ]
    
    for dep in system_deps:
        run_command(['sudo', 'apt', 'install', '-y', dep], f"安装系统包: {dep}")
    
    # Python 依赖
    python_deps = [
        'speedtest-cli',
        'cryptography',
        'requests'
    ]
    
    for dep in python_deps:
        run_command(['pip3', 'install', dep], f"安装 Python 包: {dep}")
    
    return True

def verify_installation():
    """验证安装结果"""
    print("\n🔍 验证安装结果:")
    
    tools = [
        ('speedtest-cli', '网络测速'),
        ('dig', 'DNS查询'),
        ('traceroute', '路由追踪'),
        ('openssl', 'SSL工具'),
        ('ping', 'Ping工具'),
        ('nslookup', 'DNS查询备用')
    ]
    
    results = {}
    for cmd, desc in tools:
        if check_command_exists(cmd):
            print(f"✅ {desc} ({cmd}) - 可用")
            results[cmd] = True
        else:
            print(f"❌ {desc} ({cmd}) - 不可用")
            results[cmd] = False
    
    # 检查 Python 包
    python_packages = [
        'speedtest',
        'cryptography',
        'requests'
    ]
    
    for package in python_packages:
        try:
            __import__(package)
            print(f"✅ Python 包 {package} - 可用")
            results[f"python-{package}"] = True
        except ImportError:
            print(f"❌ Python 包 {package} - 不可用")
            results[f"python-{package}"] = False
    
    return results

def main():
    """主函数"""
    print("🚀 网络诊断工具依赖安装脚本")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "darwin":
        success = install_macos_dependencies()
    elif system == "linux":
        success = install_linux_dependencies()
    else:
        print(f"❌ 不支持的操作系统: {system}")
        return 1
    
    if not success:
        print("❌ 依赖安装失败")
        return 1
    
    print("\n" + "=" * 50)
    results = verify_installation()
    
    # 统计结果
    total = len(results)
    success_count = sum(results.values())
    
    print(f"\n📊 安装结果: {success_count}/{total} 成功")
    
    if success_count == total:
        print("🎉 所有依赖安装成功！")
        return 0
    else:
        print("⚠️ 部分依赖安装失败，但基本功能仍可使用")
        print("   失败的工具将使用备用方案")
        return 0

if __name__ == "__main__":
    sys.exit(main())
