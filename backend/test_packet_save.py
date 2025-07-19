#!/usr/bin/env python3
"""
测试抓包数据保存功能
"""

import asyncio
import json
import sys
import logging
from app.mcp.servers.packet_capture_server import PacketCaptureServer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_packet_save():
    """测试抓包保存功能"""
    server = PacketCaptureServer()
    
    print("=== 抓包数据保存功能测试 ===\n")
    
    # 1. 检查默认设置
    print("1. 检查默认保存设置:")
    print(f"   自动保存: {server.auto_save}")
    print(f"   保存格式: {server.save_formats}")
    print(f"   保存目录: {server.save_directory}")
    print()
    
    # 2. 测试配置修改
    print("2. 测试配置修改:")
    config_result = await server.configure_auto_save_settings(
        auto_save=True,
        save_formats=["json", "summary"]
    )
    print(f"   配置结果: {config_result}")
    print()
    
    # 3. 模拟抓包会话（创建测试数据）
    print("3. 创建测试抓包会话:")
    from datetime import datetime
    from app.mcp.servers.packet_capture_server import CaptureSession, PacketSummary
    
    # 创建测试会话
    session_id = "test_save_123456"
    session = CaptureSession(
        session_id=session_id,
        start_time=datetime.now(),
        end_time=datetime.now(),
        target="baidu.com",
        filter_expr="host baidu.com",
        packets=[],
        connections={},
        is_running=False,
        process=None,
        duration=30
    )
    
    # 添加测试数据包
    test_packets = [
        PacketSummary(
            timestamp="12:34:56.789",
            protocol="TCP",
            src_ip="192.168.1.100",
            dst_ip="110.242.68.3",
            src_port=12345,
            dst_port=80,
            packet_type="HTTP_REQUEST",
            summary="GET / HTTP/1.1",
            flags=["SYN", "ACK"],
            size=64
        ),
        PacketSummary(
            timestamp="12:34:56.890",
            protocol="TCP", 
            src_ip="110.242.68.3",
            dst_ip="192.168.1.100",
            src_port=80,
            dst_port=12345,
            packet_type="HTTP_RESPONSE",
            summary="HTTP/1.1 200 OK",
            flags=["ACK"],
            size=512
        ),
        PacketSummary(
            timestamp="12:34:57.123",
            protocol="ICMP",
            src_ip="192.168.1.100",
            dst_ip="110.242.68.3", 
            src_port=None,
            dst_port=None,
            packet_type="ICMP_PING",
            summary="ping request",
            flags=[],
            size=64
        )
    ]
    
    session.packets = test_packets
    server.sessions[session_id] = session
    
    print(f"   会话ID: {session_id}")
    print(f"   测试数据包数: {len(test_packets)}")
    print()
    
    # 4. 测试手动保存
    print("4. 测试手动保存:")
    save_result = await server.save_capture_data_manual(
        session_id=session_id,
        formats=["json", "summary", "raw"]
    )
    print(f"   保存结果: {json.dumps(save_result, indent=2, ensure_ascii=False)}")
    print()
    
    # 5. 验证保存的文件
    print("5. 验证保存的文件:")
    if save_result.get("success") and save_result.get("saved_files"):
        for file_path in save_result["saved_files"]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"   文件: {file_path}")
                    print(f"   大小: {len(content)} 字符")
                    print(f"   前100字符: {content[:100]}...")
                    print()
            except Exception as e:
                print(f"   读取文件 {file_path} 失败: {e}")
    
    # 6. 测试自动保存逻辑
    print("6. 测试自动保存逻辑:")
    # 清空之前的保存文件记录
    session.saved_files = []
    
    # 直接调用保存方法（模拟自动保存）
    auto_saved_files = server._save_capture_data(session)
    print(f"   自动保存文件数: {len(auto_saved_files)}")
    for file_path in auto_saved_files:
        print(f"   - {file_path}")
    print()
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    try:
        asyncio.run(test_packet_save())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试失败: {e}")
        sys.exit(1) 