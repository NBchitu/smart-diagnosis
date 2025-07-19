#!/usr/bin/env python3
"""
测试前端轮询修复
模拟前端的轮询行为，验证修复效果
"""

import requests
import time
import json

def simulate_frontend_polling():
    """模拟前端轮询行为"""
    print("🔄 模拟前端轮询行为测试")
    print("=" * 60)
    
    # 1. 创建抓包任务
    print("1️⃣ 创建抓包任务...")
    test_request = {
        "issue_type": "dns",
        "duration": 3,
        "user_description": "前端轮询修复测试",
        "enable_ai_analysis": True
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/capture',
            json=test_request,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 创建任务失败: {response.status_code}")
            return False
        
        data = response.json()
        task_id = data.get('task_id')
        print(f"   ✅ 任务创建成功: {task_id}")
        
    except Exception as e:
        print(f"❌ 创建任务异常: {str(e)}")
        return False
    
    # 2. 模拟step 2的轮询（抓包阶段）
    print("\n2️⃣ 模拟step 2轮询（抓包阶段）...")
    step = 2
    
    for i in range(20):  # 最多轮询20次
        try:
            response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
            if response.status_code != 200:
                print(f"   ❌ 状态查询失败: {response.status_code}")
                break
            
            data = response.json()
            status = data.get('status')
            progress = data.get('progress', 0)
            
            print(f"   📊 轮询 {i+1}: {status} ({progress}%)")
            
            # 模拟前端的状态转换逻辑
            if status == 'processing':
                step = 3
                print("   🔄 转换到step 3")
            elif status == 'ai_analyzing':
                step = 4
                print("   🔄 转换到step 4")
                break
            elif status == 'done':
                step = 4
                print("   🔄 转换到step 4")
                break
            elif status == 'error':
                print(f"   ❌ 任务失败: {data.get('error')}")
                return False
            
            time.sleep(1.2)  # 模拟前端的1200ms间隔
            
        except Exception as e:
            print(f"   ❌ 轮询异常: {str(e)}")
            break
    
    if step != 4:
        print("   ❌ 未能进入step 4")
        return False
    
    # 3. 模拟step 4的轮询（AI分析阶段）
    print("\n3️⃣ 模拟step 4轮询（AI分析阶段）...")
    
    result_obtained = False
    
    for i in range(30):  # 最多轮询30次
        try:
            # 先检查状态（新的修复逻辑）
            status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
            if status_response.status_code != 200:
                print(f"   ❌ 状态查询失败: {status_response.status_code}")
                break
            
            status_data = status_response.json()
            status = status_data.get('status')
            progress = status_data.get('progress', 0)
            
            print(f"   📊 step 4轮询 {i+1}: {status} ({progress}%)")
            
            if status == 'done':
                print("   ✅ 任务完成，获取结果...")
                
                # 获取结果
                result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get('result'):
                        print("   ✅ 成功获取结果")
                        result_obtained = True
                        
                        # 显示结果摘要
                        result = result_data['result']
                        if 'ai_analysis' in result:
                            ai_analysis = result['ai_analysis']
                            if ai_analysis.get('success'):
                                print("   🤖 AI分析成功")
                            else:
                                print(f"   ⚠️ AI分析失败: {ai_analysis.get('error')}")
                        
                        break
                    else:
                        print(f"   ❌ 结果获取失败: {result_data.get('error')}")
                        break
                else:
                    print(f"   ❌ 结果请求失败: {result_response.status_code}")
                    break
                    
            elif status == 'error':
                print(f"   ❌ 任务失败: {status_data.get('error')}")
                break
            elif status == 'ai_analyzing':
                print("   🤖 AI分析进行中，继续等待...")
            
            time.sleep(2)  # 模拟前端的2秒间隔
            
        except Exception as e:
            print(f"   ❌ step 4轮询异常: {str(e)}")
            break
    
    return result_obtained

def test_old_vs_new_behavior():
    """对比修复前后的行为"""
    print("\n🔍 对比修复前后的行为...")
    
    # 模拟修复前的行为（只调用一次result API）
    print("\n   修复前的行为模拟:")
    test_request = {
        "issue_type": "slow",
        "duration": 2,
        "user_description": "修复前行为测试",
        "enable_ai_analysis": True
    }
    
    try:
        response = requests.post('http://localhost:8000/api/capture', json=test_request)
        if response.status_code == 200:
            task_id = response.json().get('task_id')
            
            # 等待一段时间让任务进入ai_analyzing状态
            time.sleep(5)
            
            # 模拟修复前：直接调用result API
            result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
            if result_response.status_code == 200:
                result_data = result_response.json()
                if 'error' in result_data and result_data['error'] == '任务未完成':
                    print("   ❌ 修复前：获取到'任务未完成'错误，前端会停止轮询")
                    
                    # 继续等待看任务是否会完成
                    time.sleep(10)
                    final_status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
                    if final_status_response.status_code == 200:
                        final_status = final_status_response.json().get('status')
                        print(f"   📊 10秒后任务状态: {final_status}")
                        
                        if final_status == 'done':
                            print("   ✅ 任务实际上已完成，但修复前的前端错过了结果")
                            return True
                        else:
                            print("   ⚠️ 任务仍在进行中")
                            
    except Exception as e:
        print(f"   ❌ 对比测试异常: {str(e)}")
    
    return False

def main():
    """主函数"""
    print("🌟 前端轮询修复验证测试")
    print("=" * 70)
    
    # 测试修复后的轮询行为
    polling_ok = simulate_frontend_polling()
    
    # 对比修复前后的行为
    comparison_ok = test_old_vs_new_behavior()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if polling_ok:
        print("🎉 前端轮询修复成功！")
        print("\n✅ 修复效果:")
        print("   - step 4继续轮询状态而不是只调用一次result")
        print("   - 能够正确等待AI分析完成")
        print("   - 避免因'任务未完成'错误而停止轮询")
        print("   - 最终能够成功获取分析结果")
        
        if comparison_ok:
            print("\n🔍 对比结果:")
            print("   - 修复前：会错过已完成的任务结果")
            print("   - 修复后：能够正确获取最终结果")
        
        print("\n🎯 现在前端可以:")
        print("   - 正确处理AI分析阶段的轮询")
        print("   - 避免过早停止轮询")
        print("   - 成功获取完整的分析结果")
        
    else:
        print("❌ 前端轮询仍有问题")
        print("\n💡 可能的原因:")
        print("   - 后端任务仍然卡住")
        print("   - API响应格式问题")
        print("   - 轮询逻辑仍有缺陷")
    
    return polling_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
