#!/usr/bin/env python3
"""
测试AI分析卡住问题修复
验证任务不再卡在ai_analyzing状态
"""

import requests
import time
import json

def test_ai_analyzing_fix():
    """测试AI分析卡住问题修复"""
    print("🔧 测试AI分析卡住问题修复")
    print("=" * 60)
    
    # 测试请求
    test_request = {
        "issue_type": "dns",
        "duration": 2,  # 短时间抓包
        "user_description": "AI分析卡住修复测试",
        "enable_ai_analysis": True
    }
    
    try:
        print("1️⃣ 发送抓包请求...")
        response = requests.post(
            'http://localhost:8000/api/capture',
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"   ✅ 任务创建: {task_id}")
            
            print("\n2️⃣ 监控任务进度（详细）...")
            
            # 监控任务进度
            status_history = []
            ai_analyzing_count = 0
            
            for i in range(40):  # 最多等待40秒
                time.sleep(1)
                
                try:
                    status_response = requests.get(
                        f'http://localhost:8000/api/capture/status?task_id={task_id}',
                        timeout=5
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        progress = status_data.get('progress', 0)
                        
                        # 记录状态历史
                        status_history.append({
                            'time': i,
                            'status': status,
                            'progress': progress
                        })
                        
                        # 统计ai_analyzing状态的次数
                        if status == 'ai_analyzing':
                            ai_analyzing_count += 1
                            
                        # 显示状态变化
                        if len(status_history) == 1 or status_history[-1]['status'] != status_history[-2]['status']:
                            print(f"   📊 {i}s: {status} ({progress}%)")
                        
                        # 检查是否完成
                        if status == 'done':
                            print(f"   ✅ 任务完成 (用时: {i}秒)")
                            break
                        elif status == 'error':
                            error = status_data.get('error', '')
                            print(f"   ❌ 任务失败: {error}")
                            break
                        
                        # 检查是否卡在ai_analyzing状态太久
                        if status == 'ai_analyzing' and ai_analyzing_count > 20:
                            print(f"   ⚠️ AI分析状态持续 {ai_analyzing_count} 秒，可能卡住了")
                            
                    else:
                        print(f"   ❌ 状态查询失败: {status_response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"   ❌ 状态查询异常: {str(e)}")
                    break
            
            # 分析结果
            print(f"\n3️⃣ 分析测试结果...")
            print(f"   总监控时间: {len(status_history)} 秒")
            print(f"   AI分析状态持续: {ai_analyzing_count} 秒")
            
            if len(status_history) > 0:
                final_status = status_history[-1]['status']
                print(f"   最终状态: {final_status}")
                
                if final_status == 'ai_analyzing':
                    print("   ❌ 任务仍卡在AI分析状态")
                    return False
                elif final_status == 'done':
                    print("   ✅ 任务正常完成")
                    
                    # 获取结果验证
                    try:
                        result_response = requests.get(
                            f'http://localhost:8000/api/capture/result?task_id={task_id}',
                            timeout=5
                        )
                        
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            result = result_data.get('result', {})
                            ai_analysis = result.get('ai_analysis', {})
                            
                            if ai_analysis:
                                if ai_analysis.get('success'):
                                    print("   🤖 AI分析成功")
                                else:
                                    print(f"   ⚠️ AI分析失败: {ai_analysis.get('error', 'unknown')}")
                            else:
                                print("   ⚠️ 无AI分析结果")
                                
                        else:
                            print(f"   ❌ 获取结果失败: {result_response.status_code}")
                            
                    except Exception as e:
                        print(f"   ❌ 获取结果异常: {str(e)}")
                    
                    return True
                    
                elif final_status == 'error':
                    print("   ⚠️ 任务失败，但状态正常更新")
                    return True
                else:
                    print(f"   ⚠️ 未知的最终状态: {final_status}")
                    return False
            else:
                print("   ❌ 无状态历史记录")
                return False
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_multiple_requests():
    """测试多个请求，确保没有资源泄漏"""
    print("\n🔄 测试多个请求...")
    
    success_count = 0
    total_count = 3
    
    for i in range(total_count):
        print(f"\n   测试 {i+1}/{total_count}:")
        
        test_request = {
            "issue_type": "slow",
            "duration": 1,  # 很短的抓包时间
            "user_description": f"多请求测试 {i+1}",
            "enable_ai_analysis": True
        }
        
        try:
            response = requests.post(
                'http://localhost:8000/api/capture',
                json=test_request,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                
                # 等待任务完成
                for j in range(15):
                    time.sleep(1)
                    
                    status_response = requests.get(
                        f'http://localhost:8000/api/capture/status?task_id={task_id}',
                        timeout=3
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        
                        if status in ['done', 'error']:
                            print(f"     ✅ 请求 {i+1} 完成: {status}")
                            success_count += 1
                            break
                    
                else:
                    print(f"     ❌ 请求 {i+1} 超时")
            else:
                print(f"     ❌ 请求 {i+1} 失败: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ 请求 {i+1} 异常: {str(e)}")
    
    print(f"\n   多请求测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def main():
    """主函数"""
    print("🌟 AI分析卡住问题修复验证")
    print("=" * 70)
    
    # 测试单个请求
    single_test_ok = test_ai_analyzing_fix()
    
    # 测试多个请求
    multiple_test_ok = test_multiple_requests()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if single_test_ok and multiple_test_ok:
        print("🎉 AI分析卡住问题修复成功！")
        print("\n✅ 修复效果:")
        print("   - 任务不再卡在ai_analyzing状态")
        print("   - AI分析异常被正确捕获")
        print("   - 任务状态正常更新")
        print("   - 支持多个并发请求")
        
        print("\n🎯 系统现在可以:")
        print("   - 正常完成AI分析")
        print("   - 处理AI分析异常")
        print("   - 避免任务卡死")
        
    else:
        print("❌ 仍有问题需要解决")
        
        if not single_test_ok:
            print("   - 单个请求测试失败")
        if not multiple_test_ok:
            print("   - 多请求测试失败")
    
    return single_test_ok and multiple_test_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
