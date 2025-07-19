#!/usr/bin/env python3
"""
基础网络工具测试脚本
验证系统网络工具是否正确安装和配置
"""

import asyncio
import subprocess
import platform
import sys

async def test_ping():
    """测试ping命令"""
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "2", "baidu.com"]
        else:
            cmd = ["ping", "-c", "2", "baidu.com"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        success = process.returncode == 0
        
        print(f"✅ Ping测试: {'成功' if success else '失败'}")
        if not success:
            print(f"   错误: {stderr.decode('utf-8')[:100]}")
        return success
    except Exception as e:
        print(f"❌ Ping测试异常: {str(e)}")
        return False

async def test_speedtest():
    """测试speedtest-cli命令"""
    try:
        process = await asyncio.create_subprocess_exec(
            "speedtest-cli", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        success = process.returncode == 0
        
        print(f"✅ Speedtest工具: {'已安装' if success else '未安装'}")
        if success:
            version = stdout.decode('utf-8').strip()
            print(f"   版本: {version}")
        else:
            print("   建议: pip install speedtest-cli")
        return success
    except FileNotFoundError:
        print("❌ Speedtest工具: 未找到")
        print("   建议: pip install speedtest-cli")
        return False
    except Exception as e:
        print(f"❌ Speedtest测试异常: {str(e)}")
        return False

async def test_nslookup():
    """测试nslookup命令"""
    try:
        process = await asyncio.create_subprocess_exec(
            "nslookup", "baidu.com",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        success = process.returncode == 0
        
        print(f"✅ DNS查询: {'成功' if success else '失败'}")
        if not success:
            print(f"   错误: {stderr.decode('utf-8')[:100]}")
        return success
    except Exception as e:
        print(f"❌ DNS查询异常: {str(e)}")
        return False

async def test_network_interfaces():
    """测试网络接口命令"""
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ipconfig"]
        else:
            cmd = ["ifconfig"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        success = process.returncode == 0
        
        print(f"✅ 网络接口查询: {'成功' if success else '失败'}")
        if not success:
            print(f"   错误: {stderr.decode('utf-8')[:100]}")
        return success
    except Exception as e:
        print(f"❌ 网络接口查询异常: {str(e)}")
        return False

async def test_traceroute():
    """测试traceroute命令"""
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["tracert", "-h", "3", "baidu.com"]
        else:
            cmd = ["traceroute", "-m", "3", "baidu.com"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            success = process.returncode == 0
        except asyncio.TimeoutError:
            process.kill()
            success = False
            print("   超时终止")
        
        print(f"✅ 路径追踪: {'成功' if success else '失败/超时'}")
        return success
    except Exception as e:
        print(f"❌ 路径追踪异常: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🔧 AI网络诊断系统 - 基础工具验证")
    print("=" * 50)
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version.split()[0]}")
    print()
    
    # 执行所有测试
    tests = [
        ("基础连通性测试", test_ping()),
        ("速度测试工具", test_speedtest()),
        ("DNS解析测试", test_nslookup()),
        ("网络接口查询", test_network_interfaces()),
        ("路径追踪测试", test_traceroute())
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有基础工具测试通过！系统已准备好进行AI诊断。")
        return True
    else:
        print("⚠️  部分工具测试失败，请检查系统配置。")
        print("\n💡 建议:")
        print("   1. 安装缺失的网络工具")
        print("   2. 检查系统权限")
        print("   3. 验证网络连接")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)