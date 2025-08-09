"""
端口扫描 API
支持 macOS 和树莓派 5 系统
"""

import socket
import time
import threading
import subprocess
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
import concurrent.futures

router = APIRouter()

class PortScanRequest(BaseModel):
    target: str
    ports: List[int] = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
    scan_type: str = "tcp"  # tcp, udp, syn
    timeout: int = 3

class PortScanResult(BaseModel):
    port: int
    status: str  # 'open', 'closed', 'filtered', 'timeout'
    service: Optional[str] = None
    response_time: Optional[float] = None
    banner: Optional[str] = None

class PortScanResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    details: Optional[str] = None

# 常见端口服务映射
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    993: "IMAPS",
    995: "POP3S",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    3389: "RDP",
    5432: "PostgreSQL",
    3306: "MySQL",
    1433: "MSSQL",
    6379: "Redis",
    27017: "MongoDB"
}

def get_service_name(port: int) -> str:
    """获取端口对应的服务名称"""
    return COMMON_PORTS.get(port, f"Port-{port}")

def scan_tcp_port(target: str, port: int, timeout: int = 3) -> PortScanResult:
    """扫描单个 TCP 端口"""
    start_time = time.time()
    
    try:
        # 解析目标地址
        target_ip = socket.gethostbyname(target)
        
        # 创建 socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # 尝试连接
        result = sock.connect_ex((target_ip, port))
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        sock.close()
        
        if result == 0:
            # 端口开放，尝试获取 banner
            banner = get_port_banner(target_ip, port, timeout=1)
            return PortScanResult(
                port=port,
                status="open",
                service=get_service_name(port),
                response_time=response_time,
                banner=banner
            )
        else:
            return PortScanResult(
                port=port,
                status="closed",
                service=get_service_name(port),
                response_time=response_time
            )
            
    except socket.timeout:
        return PortScanResult(
            port=port,
            status="timeout",
            service=get_service_name(port),
            response_time=timeout * 1000
        )
    except Exception as e:
        return PortScanResult(
            port=port,
            status="filtered",
            service=get_service_name(port),
            response_time=0
        )

def get_port_banner(target_ip: str, port: int, timeout: int = 1) -> Optional[str]:
    """尝试获取端口的 banner 信息"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target_ip, port))
        
        # 发送简单的请求
        if port == 80 or port == 8080:
            sock.send(b"GET / HTTP/1.0\r\n\r\n")
        elif port == 21:
            pass  # FTP 服务器通常会主动发送欢迎信息
        elif port == 22:
            pass  # SSH 服务器会发送版本信息
        
        # 接收响应
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        
        return banner[:200] if banner else None  # 限制 banner 长度

    except:
        return None

def scan_udp_port(target: str, port: int, timeout: int = 3) -> PortScanResult:
    """扫描单个 UDP 端口（简单实现）"""
    start_time = time.time()

    try:
        target_ip = socket.gethostbyname(target)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)

        # 发送空数据包
        sock.sendto(b"", (target_ip, port))

        try:
            # 尝试接收响应
            data, addr = sock.recvfrom(1024)
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)

            return PortScanResult(
                port=port,
                status="open",
                service=get_service_name(port),
                response_time=response_time
            )
        except socket.timeout:
            # UDP 端口可能开放但不响应
            return PortScanResult(
                port=port,
                status="open|filtered",
                service=get_service_name(port),
                response_time=timeout * 1000
            )
        finally:
            sock.close()

    except Exception as e:
        return PortScanResult(
            port=port,
            status="filtered",
            service=get_service_name(port),
            response_time=0
        )

def run_port_scan(target: str, ports: List[int], scan_type: str = "tcp", timeout: int = 3) -> Dict[str, Any]:
    """执行端口扫描"""
    start_time = time.time()

    try:
        # 解析目标IP
        target_ip = socket.gethostbyname(target)

        # 使用线程池并发扫描
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            if scan_type.lower() == "tcp":
                futures = {executor.submit(scan_tcp_port, target, port, timeout): port for port in ports}
            elif scan_type.lower() == "udp":
                futures = {executor.submit(scan_udp_port, target, port, timeout): port for port in ports}
            else:
                raise ValueError(f"不支持的扫描类型: {scan_type}")

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    port = futures[future]
                    results.append(PortScanResult(
                        port=port,
                        status="error",
                        service=get_service_name(port),
                        response_time=0
                    ))

        end_time = time.time()
        scan_duration = round(end_time - start_time, 2)

        # 分类结果
        open_ports = [r for r in results if r.status == "open"]
        closed_ports = [r for r in results if r.status == "closed"]
        filtered_ports = [r for r in results if r.status in ["filtered", "timeout", "error", "open|filtered"]]

        return {
            "target": target,
            "target_ip": target_ip,
            "scan_type": scan_type,
            "ports_scanned": ports,
            "open_ports": [r.dict() for r in open_ports],
            "closed_ports": [r.dict() for r in closed_ports],
            "filtered_ports": [r.dict() for r in filtered_ports],
            "scan_duration": scan_duration,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_ports": len(ports),
                "open_count": len(open_ports),
                "closed_count": len(closed_ports),
                "filtered_count": len(filtered_ports)
            }
        }

    except Exception as e:
        raise Exception(f"端口扫描执行失败: {e}")

@router.post("/port-scan")
async def port_scan(request: PortScanRequest) -> PortScanResponse:
    """执行端口扫描"""

    try:
        print(f"🔍 开始端口扫描 - 目标: {request.target}, 端口: {len(request.ports)}个, 类型: {request.scan_type}")

        data = run_port_scan(request.target, request.ports, request.scan_type, request.timeout)

        print(f"✅ 端口扫描完成: {data['summary']['open_count']} 开放, {data['summary']['closed_count']} 关闭, {data['summary']['filtered_count']} 过滤")

        return PortScanResponse(
            success=True,
            data=data
        )

    except Exception as e:
        error_msg = str(e)
        print(f"❌ 端口扫描失败: {error_msg}")

        return PortScanResponse(
            success=False,
            error="端口扫描失败",
            details=error_msg
        )
