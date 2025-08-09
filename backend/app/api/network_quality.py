"""
网络质量监控 API
支持 macOS 和树莓派 5 系统
"""

import time
import subprocess
import statistics
import platform
import re
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
import asyncio

router = APIRouter()

class NetworkQualityRequest(BaseModel):
    target: str = "google.com"
    duration: int = 60  # 监控时长（秒）
    interval: int = 5   # 测试间隔（秒）
    include_speed_test: bool = False

class QualityMetric(BaseModel):
    timestamp: str
    ping_latency: float
    jitter: float
    packet_loss: float
    download_speed: Optional[float] = None
    upload_speed: Optional[float] = None

class NetworkQualityResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    details: Optional[str] = None

def ping_test(target: str, count: int = 4) -> Dict[str, Any]:
    """执行 ping 测试"""
    system = platform.system().lower()
    
    try:
        if system == "darwin":  # macOS
            cmd = ['ping', '-c', str(count), target]
        else:  # Linux (树莓派)
            cmd = ['ping', '-c', str(count), target]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            return {
                "success": False,
                "latency": 0,
                "jitter": 0,
                "packet_loss": 100
            }
        
        output = result.stdout
        
        # 解析延迟
        latencies = []
        if system == "darwin":
            # macOS ping 输出格式
            latency_matches = re.findall(r'time=([\d.]+)', output)
            latencies = [float(match) for match in latency_matches]
        else:
            # Linux ping 输出格式
            latency_matches = re.findall(r'time=([\d.]+)', output)
            latencies = [float(match) for match in latency_matches]
        
        # 解析丢包率
        packet_loss = 0
        loss_match = re.search(r'(\d+)% packet loss', output)
        if loss_match:
            packet_loss = float(loss_match.group(1))
        
        # 计算统计信息
        if latencies:
            avg_latency = round(statistics.mean(latencies), 2)
            jitter = round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0
        else:
            avg_latency = 0
            jitter = 0
        
        return {
            "success": True,
            "latency": avg_latency,
            "jitter": jitter,
            "packet_loss": packet_loss
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "latency": 0,
            "jitter": 0,
            "packet_loss": 100
        }
    except Exception as e:
        return {
            "success": False,
            "latency": 0,
            "jitter": 0,
            "packet_loss": 100
        }

def simple_speed_test() -> Dict[str, float]:
    """简单的速度测试"""
    try:
        import urllib.request
        import time
        
        # 测试下载速度 - 下载一个小文件
        test_url = "http://speedtest.ftp.otenet.gr/files/test1Mb.db"
        start_time = time.time()
        
        with urllib.request.urlopen(test_url, timeout=10) as response:
            data = response.read()
            
        end_time = time.time()
        duration = end_time - start_time
        file_size_mb = len(data) / (1024 * 1024)
        download_speed = round(file_size_mb / duration * 8, 2)  # 转换为 Mbps
        
        return {
            "download_speed": download_speed,
            "upload_speed": 0  # 简单测试不包含上传
        }
        
    except:
        return {
            "download_speed": 0,
            "upload_speed": 0
        }

def calculate_quality_grade(avg_latency: float, packet_loss: float, jitter: float) -> str:
    """计算网络质量等级"""
    
    # 基于延迟的评分
    if avg_latency <= 20:
        latency_score = 100
    elif avg_latency <= 50:
        latency_score = 80
    elif avg_latency <= 100:
        latency_score = 60
    elif avg_latency <= 200:
        latency_score = 40
    else:
        latency_score = 20
    
    # 基于丢包率的评分
    if packet_loss == 0:
        loss_score = 100
    elif packet_loss <= 1:
        loss_score = 80
    elif packet_loss <= 3:
        loss_score = 60
    elif packet_loss <= 5:
        loss_score = 40
    else:
        loss_score = 20
    
    # 基于抖动的评分
    if jitter <= 5:
        jitter_score = 100
    elif jitter <= 10:
        jitter_score = 80
    elif jitter <= 20:
        jitter_score = 60
    elif jitter <= 50:
        jitter_score = 40
    else:
        jitter_score = 20
    
    # 综合评分
    overall_score = (latency_score * 0.4 + loss_score * 0.4 + jitter_score * 0.2)
    
    if overall_score >= 90:
        return "Excellent"
    elif overall_score >= 75:
        return "Good"
    elif overall_score >= 60:
        return "Fair"
    else:
        return "Poor"

def generate_recommendations(summary: Dict[str, Any]) -> List[str]:
    """生成网络优化建议"""
    recommendations = []
    
    avg_latency = summary.get('avg_latency', 0)
    packet_loss = summary.get('total_packet_loss', 0)
    jitter = summary.get('avg_jitter', 0)
    
    if avg_latency > 100:
        recommendations.append("延迟较高，建议检查网络连接或更换网络服务商")
    
    if packet_loss > 1:
        recommendations.append("存在丢包现象，建议检查网络设备或联系网络服务商")
    
    if jitter > 20:
        recommendations.append("网络抖动较大，可能影响实时应用，建议优化网络配置")
    
    if summary.get('stability_score', 100) < 80:
        recommendations.append("网络稳定性较差，建议检查网络设备或网线连接")
    
    if not recommendations:
        recommendations.append("网络质量良好，无需特别优化")
    
    return recommendations

def monitor_network_quality(target: str, duration: int, interval: int, include_speed_test: bool = False) -> Dict[str, Any]:
    """监控网络质量"""
    start_time = time.time()
    metrics = []
    
    try:
        print(f"📊 开始网络质量监控 - 目标: {target}, 时长: {duration}秒, 间隔: {interval}秒")
        
        test_count = 0
        while time.time() - start_time < duration:
            test_start = time.time()
            
            # 执行 ping 测试
            ping_result = ping_test(target, count=3)
            
            # 可选的速度测试
            speed_result = {"download_speed": None, "upload_speed": None}
            if include_speed_test and test_count % 3 == 0:  # 每3次测试做一次速度测试
                speed_result = simple_speed_test()
            
            # 记录指标
            metric = QualityMetric(
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                ping_latency=ping_result["latency"],
                jitter=ping_result["jitter"],
                packet_loss=ping_result["packet_loss"],
                download_speed=speed_result.get("download_speed"),
                upload_speed=speed_result.get("upload_speed")
            )
            
            metrics.append(metric)
            test_count += 1
            
            print(f"  测试 {test_count}: 延迟 {ping_result['latency']}ms, 抖动 {ping_result['jitter']}ms, 丢包 {ping_result['packet_loss']}%")
            
            # 等待下一次测试
            elapsed = time.time() - test_start
            if elapsed < interval:
                time.sleep(interval - elapsed)
        
        # 计算统计信息
        latencies = [m.ping_latency for m in metrics if m.ping_latency > 0]
        jitters = [m.jitter for m in metrics if m.jitter > 0]
        packet_losses = [m.packet_loss for m in metrics]
        
        if latencies:
            avg_latency = round(statistics.mean(latencies), 2)
            max_latency = round(max(latencies), 2)
            min_latency = round(min(latencies), 2)
        else:
            avg_latency = max_latency = min_latency = 0
        
        avg_jitter = round(statistics.mean(jitters), 2) if jitters else 0
        total_packet_loss = round(statistics.mean(packet_losses), 2)
        
        # 计算稳定性评分
        if latencies:
            latency_variance = statistics.variance(latencies)
            stability_score = max(0, 100 - latency_variance)
        else:
            stability_score = 0
        
        stability_score = round(stability_score, 1)
        
        # 计算质量等级
        quality_grade = calculate_quality_grade(avg_latency, total_packet_loss, avg_jitter)
        
        summary = {
            "avg_latency": avg_latency,
            "max_latency": max_latency,
            "min_latency": min_latency,
            "avg_jitter": avg_jitter,
            "total_packet_loss": total_packet_loss,
            "stability_score": stability_score,
            "quality_grade": quality_grade
        }
        
        # 生成建议
        recommendations = generate_recommendations(summary)
        
        actual_duration = round(time.time() - start_time, 2)
        
        return {
            "target": target,
            "test_duration": actual_duration,
            "interval": interval,
            "metrics": [m.dict() for m in metrics],
            "summary": summary,
            "recommendations": recommendations,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise Exception(f"网络质量监控失败: {e}")

@router.post("/network-quality")
async def network_quality(request: NetworkQualityRequest) -> NetworkQualityResult:
    """执行网络质量监控"""
    
    try:
        print(f"📊 开始网络质量监控 - 目标: {request.target}, 时长: {request.duration}秒")
        
        data = monitor_network_quality(
            request.target, 
            request.duration, 
            request.interval, 
            request.include_speed_test
        )
        
        print(f"✅ 网络质量监控完成: 质量等级 {data['summary']['quality_grade']}, 稳定性 {data['summary']['stability_score']}")
        
        return NetworkQualityResult(
            success=True,
            data=data
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 网络质量监控失败: {error_msg}")
        
        return NetworkQualityResult(
            success=False,
            error="网络质量监控失败",
            details=error_msg
        )
