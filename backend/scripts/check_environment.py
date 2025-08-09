#!/usr/bin/env python3
"""
环境检测脚本
检查网络诊断工具的依赖环境
"""

import subprocess
import sys
import os
import platform

def check_command(cmd, description=""):
    """检查命令是否可用"""
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✅ {description} ({cmd}): {version}")
            return True
        else:
            print(f"❌ {description} ({cmd}): 命令执行失败")
            return False
    except FileNotFoundError:
        print(f"❌ {description} ({cmd}): 命令未找到")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} ({cmd}): 命令超时")
        return False
    except Exception as e:
        print(f"❌ {description} ({cmd}): {e}")
        return False

def check_python_module(module_name, description=""):
    """检查 Python 模块是否可用"""
    try:
        __import__(module_name)
        print(f"✅ {description} (Python {module_name}): 已安装")
        return True
    except ImportError:
        print(f"❌ {description} (Python {module_name}): 未安装")
        return False

def check_speedtest_variants():
    """检查各种 speedtest 变体"""
    print("\n🚀 检查 speedtest 工具:")
    
    variants = [
        ('speedtest-cli', 'Speedtest CLI'),
        ('speedtest', 'Speedtest (官方)'),
        ('/usr/local/bin/speedtest-cli', 'Speedtest CLI (Homebrew)'),
        (os.path.expanduser('~/.local/bin/speedtest-cli'), 'Speedtest CLI (用户目录)')
    ]
    
    found_any = False
    for cmd, desc in variants:
        if check_command(cmd, desc):
            found_any = True
    
    # 检查 Python 模块方式
    try:
        result = subprocess.run([sys.executable, '-m', 'speedtest', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Python speedtest 模块: {result.stdout.strip()}")
            found_any = True
        else:
            print("❌ Python speedtest 模块: 不可用")
    except:
        print("❌ Python speedtest 模块: 不可用")
    
    # 检查 speedtest Python 包
    if check_python_module('speedtest', 'Speedtest Python 包'):
        found_any = True
    
    return found_any

def main():
    """主函数"""
    print("🔍 网络诊断工具环境检测")
    print("=" * 50)
    
    # 系统信息
    print(f"🖥️  操作系统: {platform.system()} {platform.release()}")
    print(f"🐍 Python 版本: {sys.version}")
    print(f"📁 当前目录: {os.getcwd()}")
    print(f"🔧 Python 路径: {sys.executable}")
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("🔄 运行在虚拟环境中")
        print(f"   虚拟环境路径: {sys.prefix}")
    else:
        print("🌍 运行在系统 Python 环境中")
    
    # 检查 PATH
    print(f"\n📍 PATH 环境变量:")
    for path in os.environ.get('PATH', '').split(os.pathsep):
        if path.strip():
            print(f"   {path}")
    
    # 检查网络工具
    print("\n🌐 检查网络工具:")
    tools = [
        ('ping', 'Ping'),
        ('dig', 'DNS 查询'),
        ('nslookup', 'DNS 查询 (备用)'),
        ('traceroute', '路由追踪'),
        ('openssl', 'SSL 工具'),
        ('curl', 'HTTP 客户端'),
        ('wget', '下载工具'),
        ('nmap', '网络扫描')
    ]
    
    available_tools = 0
    for cmd, desc in tools:
        if check_command(cmd, desc):
            available_tools += 1
    
    # 检查 speedtest 工具
    speedtest_available = check_speedtest_variants()
    
    # 检查 Python 包
    print("\n🐍 检查 Python 包:")
    python_packages = [
        ('requests', 'HTTP 请求库'),
        ('urllib3', 'HTTP 库'),
        ('socket', '网络套接字'),
        ('subprocess', '进程管理'),
        ('json', 'JSON 处理'),
        ('time', '时间处理'),
        ('platform', '平台信息'),
        ('cryptography', '加密库'),
        ('ssl', 'SSL 库')
    ]
    
    available_packages = 0
    for package, desc in python_packages:
        if check_python_module(package, desc):
            available_packages += 1
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 检测结果总结:")
    print(f"   网络工具: {available_tools}/{len(tools)} 可用")
    print(f"   Python 包: {available_packages}/{len(python_packages)} 可用")
    print(f"   Speedtest: {'✅ 可用' if speedtest_available else '❌ 不可用'}")
    
    if speedtest_available and available_tools >= 6 and available_packages >= 8:
        print("\n🎉 环境检测通过！所有主要工具都可用。")
        return 0
    elif available_tools >= 4 and available_packages >= 6:
        print("\n⚠️ 环境基本可用，但部分工具缺失。")
        print("   建议运行安装脚本: python3 scripts/install_dependencies.py")
        return 0
    else:
        print("\n❌ 环境检测失败，缺少关键工具。")
        print("   请运行安装脚本: python3 scripts/install_dependencies.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
