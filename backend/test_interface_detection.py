#!/usr/bin/env python3
"""
网络接口检测测试脚本
用于验证在不同操作系统下的网络接口检测功能
"""

import platform
import subprocess
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.capture import (
    validate_interface, 
    get_default_interface, 
    list_available_interfaces,
    build_tcpdump_command
)

def test_interface_detection():
    """测试网络接口检测功能"""
    
    print("🔍 网络接口检测测试")
    print("=" * 50)
    
    # 显示系统信息
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"平台: {platform.platform()}")
    print()
    
    # 测试获取可用接口
    print("📡 获取可用网络接口:")
    try:
        interfaces = list_available_interfaces()
        if interfaces:
            print(f"✅ 发现 {len(interfaces)} 个接口: {', '.join(interfaces)}")
        else:
            print("❌ 未发现任何接口")
    except Exception as e:
        print(f"❌ 获取接口失败: {str(e)}")
    
    print()
    
    # 测试获取默认接口
    print("🎯 获取默认网络接口:")
    try:
        default_interface = get_default_interface()
        print(f"✅ 默认接口: {default_interface}")
        
        # 验证默认接口是否有效
        if validate_interface(default_interface):
            print(f"✅ 默认接口 {default_interface} 验证通过")
        else:
            print(f"❌ 默认接口 {default_interface} 验证失败")
    except Exception as e:
        print(f"❌ 获取默认接口失败: {str(e)}")
    
    print()
    
    # 测试常见接口验证
    print("🔧 测试常见接口验证:")
    if system.lower() == 'darwin':  # macOS
        test_interfaces = ['en0', 'en1', 'lo0', 'eth0']
    else:  # Linux
        test_interfaces = ['eth0', 'wlan0', 'lo', 'en0']
    
    for interface in test_interfaces:
        try:
            is_valid = validate_interface(interface)
            status = "✅" if is_valid else "❌"
            print(f"{status} {interface}: {'有效' if is_valid else '无效'}")
        except Exception as e:
            print(f"❌ {interface}: 检测失败 - {str(e)}")
    
    print()
    
    # 测试tcpdump命令构建
    print("⚙️ 测试tcpdump命令构建:")
    try:
        default_interface = get_default_interface()
        test_cases = [
            ('dns', 'port 53'),
            ('slow', 'tcp or udp port 80 or port 443'),
            ('custom', 'icmp')
        ]
        
        for issue_type, filter_expr in test_cases:
            cmd = build_tcpdump_command(
                interface=default_interface,
                output_file=f'/tmp/test_{issue_type}.pcap',
                duration=5,
                filter_expr=filter_expr
            )
            print(f"📝 {issue_type}: {cmd}")
    except Exception as e:
        print(f"❌ 命令构建失败: {str(e)}")
    
    print()
    
    # 测试tcpdump可用性
    print("🛠️ 测试tcpdump可用性:")
    try:
        result = subprocess.run(['which', 'tcpdump'], capture_output=True, text=True)
        if result.returncode == 0:
            tcpdump_path = result.stdout.strip()
            print(f"✅ tcpdump 已安装: {tcpdump_path}")
            
            # 测试tcpdump版本
            version_result = subprocess.run(['tcpdump', '--version'], 
                                          capture_output=True, text=True)
            if version_result.returncode == 0:
                version_info = version_result.stderr.split('\n')[0]  # tcpdump版本信息通常在stderr
                print(f"📋 版本信息: {version_info}")
        else:
            print("❌ tcpdump 未安装")
    except Exception as e:
        print(f"❌ tcpdump 检测失败: {str(e)}")
    
    print()
    
    # 测试权限
    print("🔐 测试权限:")
    if os.geteuid() == 0:
        print("✅ 当前以root权限运行")
    else:
        print("⚠️ 当前非root权限，抓包可能需要sudo")
        
        # 测试sudo可用性
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ sudo 可用（无需密码）")
            else:
                print("⚠️ sudo 需要密码")
        except Exception as e:
            print(f"❌ sudo 测试失败: {str(e)}")

def test_api_simulation():
    """模拟API调用测试"""
    
    print("\n🚀 API调用模拟测试")
    print("=" * 50)
    
    from app.api.capture import CaptureRequest
    
    # 创建测试请求
    test_request = CaptureRequest(
        issue_type='dns',
        duration=5,
        interface=None,  # 测试自动检测
        user_description='测试DNS解析',
        enable_ai_analysis=False
    )
    
    print(f"📋 测试请求: {test_request}")
    
    # 测试接口自动设置
    try:
        if not test_request.interface:
            test_request.interface = get_default_interface()
            print(f"✅ 自动设置接口: {test_request.interface}")
        
        # 验证接口
        if validate_interface(test_request.interface):
            print(f"✅ 接口验证通过: {test_request.interface}")
        else:
            print(f"❌ 接口验证失败: {test_request.interface}")
            
    except Exception as e:
        print(f"❌ 接口处理失败: {str(e)}")

def main():
    """主函数"""
    
    print("🌟 网络接口检测测试工具")
    print("=" * 60)
    print(f"时间: {platform.uname()}")
    print("=" * 60)
    
    # 运行接口检测测试
    test_interface_detection()
    
    # 运行API模拟测试
    test_api_simulation()
    
    print("\n🎯 测试完成")
    print("💡 如果发现问题，请检查:")
    print("  1. tcpdump 是否已安装")
    print("  2. 网络接口是否正确")
    print("  3. 权限设置是否正确")

if __name__ == '__main__':
    main()
