#!/usr/bin/env python3
"""
测试抓包命令构建
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.capture import build_tcpdump_command, get_filter_by_issue

def test_command_building():
    """测试命令构建"""
    print("🚀 测试抓包命令构建\n")
    
    # 测试不同问题类型的过滤器
    issue_types = ['website_access', 'interconnection', 'game_lag']
    
    for issue_type in issue_types:
        print(f"🧪 测试 {issue_type} 问题类型:")
        
        # 获取过滤器
        filter_expr = get_filter_by_issue(issue_type)
        print(f"   过滤器: {filter_expr}")
        
        # 构建命令
        cmd = build_tcpdump_command('en0', f'/tmp/test_{issue_type}.pcap', 15, filter_expr)
        print(f"   命令: {cmd}")
        
        # 检查命令是否包含正确的组件
        if 'sudo tcpdump' in cmd:
            print("   ✅ 包含tcpdump命令")
        else:
            print("   ❌ 缺少tcpdump命令")
            
        if '-i en0' in cmd:
            print("   ✅ 包含网络接口")
        else:
            print("   ❌ 缺少网络接口")
            
        if filter_expr and filter_expr in cmd:
            print("   ✅ 包含过滤器")
        else:
            print("   ❌ 缺少过滤器")
            
        print()

def test_filter_syntax():
    """测试过滤器语法"""
    print("🔍 测试过滤器语法\n")
    
    filters = {
        'website_access': get_filter_by_issue('website_access'),
        'interconnection': get_filter_by_issue('interconnection'),
        'game_lag': get_filter_by_issue('game_lag')
    }
    
    for name, filter_expr in filters.items():
        print(f"📋 {name}:")
        print(f"   {filter_expr}")
        
        # 基本语法检查
        if filter_expr:
            # 检查是否有不匹配的括号
            open_parens = filter_expr.count('(')
            close_parens = filter_expr.count(')')
            if open_parens == close_parens:
                print("   ✅ 括号匹配")
            else:
                print("   ❌ 括号不匹配")
                
            # 检查是否有基本的tcpdump关键字
            keywords = ['tcp', 'udp', 'port', 'or', 'and']
            has_keywords = any(keyword in filter_expr for keyword in keywords)
            if has_keywords:
                print("   ✅ 包含有效关键字")
            else:
                print("   ❌ 缺少有效关键字")
        else:
            print("   ⚠️ 空过滤器")
            
        print()

def main():
    """主测试函数"""
    try:
        test_command_building()
        test_filter_syntax()
        print("🎉 命令构建测试完成！")
        return 0
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
