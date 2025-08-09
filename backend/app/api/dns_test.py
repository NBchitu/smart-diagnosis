"""
DNS 测试 API
支持 macOS 和树莓派 5 系统
"""

import time
import socket
import subprocess
import platform
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DNSServer(BaseModel):
    name: str
    ip: str
    location: str

class DNSTestRequest(BaseModel):
    domain: str
    query_type: str = "A"
    custom_servers: List[DNSServer] = []

class DNSTestResult(BaseModel):
    server: DNSServer
    domain: str
    query_type: str
    response_time: float
    status: str  # 'success', 'timeout', 'error'
    resolved_ips: Optional[List[str]] = None
    error_message: Optional[str] = None

class DNSTestResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    details: Optional[str] = None

# 预定义的 DNS 服务器列表
DEFAULT_DNS_SERVERS = [
    DNSServer(name="Google DNS", ip="8.8.8.8", location="Global"),
    DNSServer(name="Google DNS Secondary", ip="8.8.4.4", location="Global"),
    DNSServer(name="Cloudflare DNS", ip="1.1.1.1", location="Global"),
    DNSServer(name="Cloudflare DNS Secondary", ip="1.0.0.1", location="Global"),
    DNSServer(name="OpenDNS", ip="208.67.222.222", location="Global"),
    DNSServer(name="OpenDNS Secondary", ip="208.67.220.220", location="Global"),
    DNSServer(name="Quad9 DNS", ip="9.9.9.9", location="Global"),
    DNSServer(name="阿里云 DNS", ip="223.5.5.5", location="China"),
    DNSServer(name="腾讯云 DNS", ip="119.29.29.29", location="China"),
    DNSServer(name="百度 DNS", ip="180.76.76.76", location="China")
]

def test_dns_with_dig(domain: str, dns_server: str, query_type: str = "A") -> Dict[str, Any]:
    """使用 dig 命令测试 DNS 解析"""
    try:
        start_time = time.time()
        
        cmd = ['dig', f'@{dns_server}', domain, query_type, '+short', '+time=5']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # 转换为毫秒
        
        if result.returncode == 0:
            resolved_ips = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return {
                "response_time": response_time,
                "status": "success",
                "resolved_ips": resolved_ips
            }
        else:
            return {
                "response_time": response_time,
                "status": "error",
                "error_message": result.stderr.strip() or "DNS查询失败"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "response_time": 10000,  # 超时设为10秒
            "status": "timeout",
            "error_message": "DNS查询超时"
        }
    except FileNotFoundError:
        # dig 命令不存在，使用 Python 内置方法
        return test_dns_with_socket(domain, dns_server, query_type)
    except Exception as e:
        return {
            "response_time": 0,
            "status": "error",
            "error_message": str(e)
        }

def test_dns_with_socket(domain: str, dns_server: str, query_type: str = "A") -> Dict[str, Any]:
    """使用 Python socket 测试 DNS 解析（备用方案）"""
    try:
        print(f"    使用 Python socket 解析 {domain}")
        start_time = time.time()

        if query_type == "A":
            # 解析 A 记录
            resolved_ips = [socket.gethostbyname(domain)]
        elif query_type == "AAAA":
            # IPv6 解析
            try:
                result = socket.getaddrinfo(domain, None, socket.AF_INET6)
                resolved_ips = [addr[4][0] for addr in result]
            except:
                resolved_ips = []
        else:
            # 其他记录类型的简单处理，只能解析 A 记录
            resolved_ips = [socket.gethostbyname(domain)]

        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        return {
            "response_time": response_time,
            "status": "success",
            "resolved_ips": resolved_ips
        }

    except socket.gaierror as e:
        return {
            "response_time": 5000,  # 设置一个较高的响应时间表示失败
            "status": "error",
            "error_message": f"域名解析失败: {e}"
        }
    except Exception as e:
        return {
            "response_time": 5000,
            "status": "error",
            "error_message": str(e)
        }

def test_dns_with_nslookup(domain: str, dns_server: str, query_type: str = "A") -> Dict[str, Any]:
    """使用 nslookup 命令测试 DNS 解析"""
    try:
        start_time = time.time()
        
        cmd = ['nslookup', '-type=' + query_type, domain, dns_server]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        if result.returncode == 0:
            # 解析 nslookup 输出
            resolved_ips = []
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if 'Address:' in line and not line.startswith('Server:'):
                    ip = line.split('Address:')[-1].strip()
                    if ip and ip != dns_server:
                        resolved_ips.append(ip)
            
            return {
                "response_time": response_time,
                "status": "success" if resolved_ips else "error",
                "resolved_ips": resolved_ips,
                "error_message": "未找到解析结果" if not resolved_ips else None
            }
        else:
            return {
                "response_time": response_time,
                "status": "error",
                "error_message": "nslookup 查询失败"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "response_time": 10000,
            "status": "timeout",
            "error_message": "DNS查询超时"
        }
    except Exception as e:
        return {
            "response_time": 0,
            "status": "error",
            "error_message": str(e)
        }

def test_single_dns_server(domain: str, dns_server: DNSServer, query_type: str) -> DNSTestResult:
    """测试单个 DNS 服务器"""
    
    # 优先使用 dig，然后是 nslookup，最后是 socket
    result = test_dns_with_dig(domain, dns_server.ip, query_type)
    
    if result["status"] == "error" and "not found" in result.get("error_message", "").lower():
        # 如果 dig 不存在，尝试 nslookup
        result = test_dns_with_nslookup(domain, dns_server.ip, query_type)
    
    return DNSTestResult(
        server=dns_server,
        domain=domain,
        query_type=query_type,
        response_time=result["response_time"],
        status=result["status"],
        resolved_ips=result.get("resolved_ips"),
        error_message=result.get("error_message")
    )

@router.post("/dns-test")
async def dns_test(request: DNSTestRequest) -> DNSTestResponse:
    """执行 DNS 测试"""
    
    try:
        print(f"🔍 开始DNS测试 - 域名: {request.domain}, 查询类型: {request.query_type}")
        
        # 确定要测试的 DNS 服务器
        dns_servers = request.custom_servers if request.custom_servers else DEFAULT_DNS_SERVERS
        
        # 测试所有 DNS 服务器
        test_results = []
        for dns_server in dns_servers:
            print(f"  测试 DNS 服务器: {dns_server.name} ({dns_server.ip})")
            result = test_single_dns_server(request.domain, dns_server, request.query_type)
            test_results.append(result)
        
        # 计算统计信息
        successful_tests = [r for r in test_results if r.status == "success"]
        total_tests = len(test_results)
        success_rate = round(len(successful_tests) / total_tests * 100, 1) if total_tests > 0 else 0
        
        # 找出最快和最慢的服务器
        if successful_tests:
            fastest = min(successful_tests, key=lambda x: x.response_time)
            slowest = max(successful_tests, key=lambda x: x.response_time)
            avg_response_time = round(sum(r.response_time for r in successful_tests) / len(successful_tests), 2)
        else:
            fastest = slowest = test_results[0] if test_results else None
            avg_response_time = 0
        
        data = {
            "domain": request.domain,
            "test_results": [result.dict() for result in test_results],
            "summary": {
                "fastest_server": fastest.server.dict() if fastest else None,
                "slowest_server": slowest.server.dict() if slowest else None,
                "avg_response_time": avg_response_time,
                "success_rate": success_rate,
                "total_tests": total_tests
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"✅ DNS测试完成: {len(successful_tests)}/{total_tests} 成功, 平均响应时间: {avg_response_time}ms")
        
        return DNSTestResponse(
            success=True,
            data=data
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ DNS测试失败: {error_msg}")
        
        return DNSTestResponse(
            success=False,
            error="DNS测试失败",
            details=error_msg
        )
