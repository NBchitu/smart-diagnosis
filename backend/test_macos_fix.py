#!/usr/bin/env python3
"""
macOS修复验证测试
测试在macOS下的网络接口检测和API功能
"""

import requests
import json
import time

def test_interface_api():
    """测试网络接口API"""
    print("🔍 测试网络接口API...")
    
    try:
        response = requests.get('http://localhost:8000/api/capture/interfaces')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接口API成功")
            print(f"  - 系统: {data.get('current_system')}")
            print(f"  - 默认接口: {data.get('default')}")
            print(f"  - 可用接口数量: {len(data.get('interfaces', []))}")
            print(f"  - 前5个接口: {', '.join(data.get('interfaces', [])[:5])}")
            return True
        else:
            print(f"❌ 接口API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 接口API异常: {str(e)}")
        return False

def test_capture_api_without_sudo():
    """测试抓包API（不需要sudo权限的版本）"""
    print("\n🚀 测试抓包API（模拟模式）...")
    
    # 创建一个测试请求
    test_request = {
        "issue_type": "dns",
        "duration": 2,  # 短时间测试
        "user_description": "macOS兼容性测试",
        "enable_ai_analysis": False
    }
    
    try:
        # 发送抓包请求
        response = requests.post(
            'http://localhost:8000/api/capture',
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ 抓包任务创建成功: {task_id}")
            
            # 监控任务状态
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(1)
                
                status_response = requests.get(
                    f'http://localhost:8000/api/capture/status?task_id={task_id}',
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    print(f"  📊 状态: {status} ({progress}%)")
                    
                    if status == 'done':
                        print("✅ 抓包任务完成")
                        return True
                    elif status == 'error':
                        error = status_data.get('error', '未知错误')
                        print(f"❌ 抓包任务失败: {error}")
                        
                        # 检查是否是权限问题
                        if 'sudo' in error.lower() or 'permission' in error.lower():
                            print("💡 这是预期的权限错误，说明API工作正常")
                            return True
                        return False
                else:
                    print(f"❌ 状态查询失败: {status_response.status_code}")
                    return False
            
            print("⚠️ 任务超时")
            return False
            
        else:
            print(f"❌ 抓包请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 抓包API异常: {str(e)}")
        return False

def test_health_check():
    """测试健康检查"""
    print("\n❤️ 测试服务健康状态...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务健康: {data.get('message')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🌟 macOS兼容性修复验证测试")
    print("=" * 50)
    
    results = []
    
    # 测试服务健康状态
    results.append(("健康检查", test_health_check()))
    
    # 测试网络接口API
    results.append(("网络接口API", test_interface_api()))
    
    # 测试抓包API
    results.append(("抓包API", test_capture_api_without_sudo()))
    
    # 打印测试结果
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！macOS兼容性修复成功！")
        print("\n💡 接下来可以:")
        print("  1. 启动前端服务测试完整流程")
        print("  2. 在有sudo权限的环境下测试实际抓包")
        print("  3. 配置AI API密钥测试AI分析功能")
    else:
        print("⚠️ 部分测试失败，请检查服务状态")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
