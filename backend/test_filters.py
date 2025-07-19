#!/usr/bin/env python3
"""
测试抓包过滤器语法
"""

import subprocess
import sys

def test_filter_syntax(filter_expr, name):
    """测试过滤器语法是否正确"""
    print(f"🧪 测试 {name} 过滤器...")
    print(f"   表达式: {filter_expr}")
    
    try:
        # 使用tcpdump -d 来验证语法（不实际抓包）
        result = subprocess.run([
            'tcpdump', '-d', filter_expr
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(f"   ✅ 语法正确")
            return True
        else:
            print(f"   ❌ 语法错误: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ 测试超时")
        return False
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试抓包过滤器语法\n")
    
    # 测试所有过滤器
    filters = {
        'website_access': 'tcp port 80 or port 443 or port 8080 or port 8443',
        'interconnection': 'tcp or udp',
        'game_lag': 'udp or tcp port 7000 or port 8001 or port 17500 or port 27015 or port 25565 or port 10012',
        'simple_game': 'udp or tcp port 7000',
        'simple_web': 'tcp port 80 or port 443'
    }
    
    results = {}
    for name, filter_expr in filters.items():
        results[name] = test_filter_syntax(filter_expr, name)
        print()
    
    # 总结结果
    print("📊 测试结果总结:")
    passed = sum(results.values())
    total = len(results)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 总计: {passed}/{total} 个过滤器通过测试")
    
    if passed == total:
        print("🎉 所有过滤器语法正确！")
        return 0
    else:
        print("⚠️ 部分过滤器需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
