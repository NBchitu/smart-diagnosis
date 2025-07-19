#!/usr/bin/env python3
"""
简化的过滤器测试
"""

def get_filter_by_issue(issue_type: str) -> str:
    """根据问题类型生成抓包过滤表达式"""
    base_filters = {
        'website_access': 'tcp port 80 or port 443 or port 8080 or port 8443',
        'interconnection': 'tcp or udp',
        'game_lag': 'udp or (tcp and (port 7000 or port 8001 or port 17500 or port 27015 or port 25565 or port 10012))',
        'custom': ''
    }
    return base_filters.get(issue_type, '')

def build_tcpdump_command(interface: str, output_file: str, duration: int, filter_expr: str) -> str:
    """构建tcpdump命令"""
    import platform
    system = platform.system().lower()

    if system == 'darwin':  # macOS
        cmd_parts = [
            'sudo', 'tcpdump',
            '-i', interface,
            '-w', output_file,
            '-s', '65535',
            '-q'
        ]

        if filter_expr:
            cmd_parts.append(filter_expr)

        return ' '.join(cmd_parts)
    else:  # Linux
        cmd_parts = [
            'sudo', 'tcpdump',
            '-i', interface,
            '-w', output_file,
            '-G', str(duration),
            '-W', '1',
            '-s', '65535',
            '-q'
        ]

        if filter_expr:
            cmd_parts.append(filter_expr)

        return ' '.join(cmd_parts)

def test_filters():
    """测试过滤器"""
    print("🧪 测试抓包过滤器\n")
    
    issue_types = ['website_access', 'interconnection', 'game_lag']
    
    for issue_type in issue_types:
        print(f"📋 {issue_type}:")
        filter_expr = get_filter_by_issue(issue_type)
        print(f"   过滤器: {filter_expr}")
        
        # 构建命令
        cmd = build_tcpdump_command('en0', f'/tmp/test_{issue_type}.pcap', 15, filter_expr)
        print(f"   命令: {cmd}")
        
        # 检查语法
        if 'or' in filter_expr and 'port' in filter_expr:
            print("   ✅ 语法看起来正确")
        elif filter_expr == 'tcp or udp':
            print("   ✅ 简单语法正确")
        elif not filter_expr:
            print("   ⚠️ 空过滤器")
        else:
            print("   ❓ 需要进一步验证")
            
        print()

def main():
    """主函数"""
    test_filters()
    print("🎉 测试完成！")

if __name__ == "__main__":
    main()
