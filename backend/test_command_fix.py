#!/usr/bin/env python3
"""
测试tcpdump命令构建修复
验证shell命令语法正确性
"""

import sys
import os
import subprocess

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.capture import (
    build_tcpdump_command,
    get_filter_by_issue,
    get_default_interface
)

def test_command_syntax():
    """测试命令语法正确性"""
    print("🔧 测试tcpdump命令构建...")
    
    interface = get_default_interface()
    test_cases = [
        ('slow', '网速慢'),
        ('dns', 'DNS解析'),
        ('disconnect', '连接问题'),
        ('lan', '局域网问题'),
        ('video', '视频问题')
    ]
    
    for issue_type, description in test_cases:
        print(f"\n📋 测试 {description} ({issue_type}):")
        
        try:
            # 生成过滤表达式
            filter_expr = get_filter_by_issue(issue_type)
            print(f"  过滤表达式: {filter_expr}")
            
            # 构建命令
            cmd = build_tcpdump_command(
                interface=interface,
                output_file=f'/tmp/test_{issue_type}.pcap',
                duration=5,
                filter_expr=filter_expr
            )
            print(f"  完整命令: {cmd}")
            
            # 测试命令语法（不实际执行tcpdump）
            # 我们只测试shell能否正确解析命令
            test_cmd = cmd.replace('sudo tcpdump', 'echo "tcpdump"')
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ 命令语法正确")
            else:
                print(f"  ❌ 命令语法错误: {result.stderr}")
                
        except Exception as e:
            print(f"  ❌ 测试异常: {str(e)}")

def test_filter_expressions():
    """测试过滤表达式"""
    print("\n🎯 测试过滤表达式生成...")
    
    test_cases = [
        ('slow', None, None, None),
        ('dns', '8.8.8.8', None, None),
        ('slow', None, 80, None),
        ('custom', None, None, 'icmp'),
        ('dns', '1.1.1.1', 53, None)
    ]
    
    for issue_type, target_ip, target_port, custom_filter in test_cases:
        try:
            filter_expr = get_filter_by_issue(issue_type, target_ip, target_port, custom_filter)
            print(f"  {issue_type} + IP:{target_ip} + Port:{target_port} + Custom:{custom_filter}")
            print(f"    → {filter_expr}")
        except Exception as e:
            print(f"  ❌ 过滤表达式生成失败: {str(e)}")

def test_api_simulation():
    """模拟API调用测试"""
    print("\n🚀 模拟API调用测试...")
    
    import requests
    import json
    import time
    
    # 测试请求
    test_request = {
        "issue_type": "slow",
        "duration": 2,
        "user_description": "命令修复测试",
        "enable_ai_analysis": False
    }
    
    try:
        print("发送抓包请求...")
        response = requests.post(
            'http://localhost:8000/api/capture',
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ 任务创建成功: {task_id}")
            
            # 监控任务状态
            for i in range(8):
                time.sleep(1)
                
                status_response = requests.get(
                    f'http://localhost:8000/api/capture/status?task_id={task_id}',
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    print(f"  状态: {status} ({progress}%)")
                    
                    if status == 'error':
                        error = status_data.get('error', '')
                        print(f"  错误: {error}")
                        
                        # 检查是否还有语法错误
                        if 'syntax error' in error:
                            print("  ❌ 仍然存在语法错误")
                            return False
                        elif 'sudo' in error or 'password' in error:
                            print("  ✅ 只是权限问题，命令语法正确")
                            return True
                        else:
                            print("  ⚠️ 其他错误")
                            return False
                    elif status == 'done':
                        print("  ✅ 任务完成")
                        return True
                else:
                    print(f"  ❌ 状态查询失败: {status_response.status_code}")
                    return False
            
            print("  ⚠️ 任务超时")
            return False
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API测试异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🌟 tcpdump命令修复验证测试")
    print("=" * 50)
    
    # 测试命令语法
    test_command_syntax()
    
    # 测试过滤表达式
    test_filter_expressions()
    
    # 测试API
    api_success = test_api_simulation()
    
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print("=" * 50)
    
    if api_success:
        print("✅ 命令语法修复成功！")
        print("💡 现在可以正常使用抓包功能了")
    else:
        print("❌ 仍然存在问题，需要进一步调试")
    
    return api_success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
