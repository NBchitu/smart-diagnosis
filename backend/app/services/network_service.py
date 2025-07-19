import asyncio
import subprocess
import time
import json
from typing import Dict, List, Optional
import speedtest
import ping3
import psutil

class NetworkService:
    def __init__(self):
        self.test_results = {}  # 存储测试结果
        
    async def get_network_status(self) -> Dict:
        """获取网络基本状态"""
        try:
            # 获取网络接口状态
            interfaces = psutil.net_if_stats()
            addresses = psutil.net_if_addrs()
            
            status = {
                "connected": False,
                "interfaces": {},
                "default_gateway": None,
                "dns_servers": []
            }
            
            # 检查每个网络接口
            for interface, stats in interfaces.items():
                if stats.isup and interface in addresses:
                    interface_info = {
                        "name": interface,
                        "is_up": stats.isup,
                        "speed": stats.speed,
                        "mtu": stats.mtu,
                        "addresses": []
                    }
                    
                    # 获取IP地址
                    for addr in addresses[interface]:
                        if addr.family.name == 'AF_INET':  # IPv4
                            interface_info["addresses"].append({
                                "ip": addr.address,
                                "netmask": addr.netmask,
                                "type": "IPv4"
                            })
                            if not addr.address.startswith('127.'):
                                status["connected"] = True
                    
                    status["interfaces"][interface] = interface_info
            
            return status
            
        except Exception as e:
            raise Exception(f"获取网络状态失败: {str(e)}")
    
    async def run_speed_test(self, test_id: str, servers: Optional[List[str]] = None, 
                           download_test: bool = True, upload_test: bool = True):
        """运行速度测试"""
        try:
            # 初始化测试结果
            self.test_results[test_id] = {
                "test_id": test_id,
                "test_type": "speed_test",
                "status": "running",
                "progress": 0,
                "results": None,
                "timestamp": int(time.time()),
                "error": None
            }
            
            # 更新进度: 初始化
            self.test_results[test_id]["progress"] = 10
            
            # 创建speedtest实例
            st = speedtest.Speedtest()
            
            # 更新进度: 获取服务器列表
            self.test_results[test_id]["progress"] = 20
            st.get_servers()
            
            # 选择最佳服务器
            self.test_results[test_id]["progress"] = 30
            st.get_best_server()
            
            results = {
                "server": {
                    "name": st.best["sponsor"],
                    "location": f"{st.best['name']}, {st.best['country']}",
                    "distance": st.best["d"],
                    "latency": st.best["latency"]
                }
            }
            
            # 下载测试
            if download_test:
                self.test_results[test_id]["progress"] = 50
                download_speed = st.download()
                results["download"] = {
                    "speed_bps": download_speed,
                    "speed_mbps": download_speed / 1_000_000
                }
            
            # 上传测试
            if upload_test:
                self.test_results[test_id]["progress"] = 80
                upload_speed = st.upload()
                results["upload"] = {
                    "speed_bps": upload_speed,
                    "speed_mbps": upload_speed / 1_000_000
                }
            
            # 完成测试
            self.test_results[test_id].update({
                "status": "completed",
                "progress": 100,
                "results": results
            })
            
        except Exception as e:
            self.test_results[test_id].update({
                "status": "failed",
                "error": str(e)
            })
    
    async def run_ping_test(self, test_id: str, hosts: List[str], count: int = 10):
        """运行ping测试"""
        try:
            # 初始化测试结果
            self.test_results[test_id] = {
                "test_id": test_id,
                "test_type": "ping_test",
                "status": "running",
                "progress": 0,
                "results": None,
                "timestamp": int(time.time()),
                "error": None
            }
            
            results = {"hosts": {}}
            total_hosts = len(hosts)
            
            for i, host in enumerate(hosts):
                host_results = {
                    "host": host,
                    "packets_sent": count,
                    "packets_received": 0,
                    "packet_loss": 0,
                    "avg_latency": 0,
                    "min_latency": float('inf'),
                    "max_latency": 0,
                    "latencies": []
                }
                
                # 执行ping测试
                successful_pings = 0
                total_latency = 0
                
                for j in range(count):
                    try:
                        latency = ping3.ping(host, timeout=3)
                        if latency is not None:
                            latency_ms = latency * 1000  # 转换为毫秒
                            host_results["latencies"].append(latency_ms)
                            host_results["min_latency"] = min(host_results["min_latency"], latency_ms)
                            host_results["max_latency"] = max(host_results["max_latency"], latency_ms)
                            total_latency += latency_ms
                            successful_pings += 1
                    except:
                        pass
                
                # 计算统计信息
                host_results["packets_received"] = successful_pings
                host_results["packet_loss"] = ((count - successful_pings) / count) * 100
                
                if successful_pings > 0:
                    host_results["avg_latency"] = total_latency / successful_pings
                else:
                    host_results["min_latency"] = 0
                
                results["hosts"][host] = host_results
                
                # 更新进度
                progress = int(((i + 1) / total_hosts) * 100)
                self.test_results[test_id]["progress"] = progress
            
            # 完成测试
            self.test_results[test_id].update({
                "status": "completed",
                "progress": 100,
                "results": results
            })
            
        except Exception as e:
            self.test_results[test_id].update({
                "status": "failed",
                "error": str(e)
            })
    
    async def run_traceroute(self, test_id: str, target: str):
        """运行路由跟踪"""
        try:
            # 初始化测试结果
            self.test_results[test_id] = {
                "test_id": test_id,
                "test_type": "traceroute",
                "status": "running",
                "progress": 0,
                "results": None,
                "timestamp": int(time.time()),
                "error": None
            }
            
            # 执行traceroute命令
            cmd = ["traceroute", "-m", "30", target]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                results = {
                    "target": target,
                    "hops": [],
                    "raw_output": stdout
                }
                
                # 解析traceroute输出
                lines = stdout.strip().split('\n')[1:]  # 跳过第一行
                for line in lines:
                    if line.strip():
                        results["hops"].append(line.strip())
                
                self.test_results[test_id].update({
                    "status": "completed",
                    "progress": 100,
                    "results": results
                })
            else:
                raise Exception(f"Traceroute失败: {stderr}")
                
        except Exception as e:
            self.test_results[test_id].update({
                "status": "failed",
                "error": str(e)
            })
    
    async def get_test_result(self, test_id: str) -> Optional[Dict]:
        """获取测试结果"""
        return self.test_results.get(test_id)
    
    async def get_all_tests(self) -> List[Dict]:
        """获取所有测试结果"""
        return list(self.test_results.values())
    
    async def delete_test(self, test_id: str) -> bool:
        """删除测试结果"""
        if test_id in self.test_results:
            del self.test_results[test_id]
            return True
        return False

    async def check_internet_connectivity(self) -> Dict:
        """检测网络与互联网的连通性"""
        try:
            connectivity_result = {
                "local_network": False,
                "internet_dns": False,
                "internet_http": False,
                "details": {
                    "gateway_reachable": False,
                    "dns_resolution": False,
                    "external_ping": False,
                    "http_response": False
                },
                "latency": {},
                "gateway_info": {
                    "ip": None,
                    "interface": None,
                    "reachable": False
                },
                "timestamp": int(time.time())
            }
            
            # 1. 检查本地网关连通性
            try:
                # 获取默认网关
                import netifaces
                gateways = netifaces.gateways()
                default_gateway_info = gateways['default'][netifaces.AF_INET]
                default_gateway = default_gateway_info[0]
                gateway_interface = default_gateway_info[1]
                
                # 保存网关信息
                connectivity_result["gateway_info"]["ip"] = default_gateway
                connectivity_result["gateway_info"]["interface"] = gateway_interface
                
                print(f"检测网关: {default_gateway} (接口: {gateway_interface})")
                
                # ping网关
                gateway_latency = ping3.ping(default_gateway, timeout=3)
                if gateway_latency is not None:
                    connectivity_result["local_network"] = True
                    connectivity_result["details"]["gateway_reachable"] = True
                    connectivity_result["gateway_info"]["reachable"] = True
                    connectivity_result["latency"]["gateway"] = gateway_latency * 1000
                    print(f"网关可达，延迟: {gateway_latency * 1000:.1f}ms")
                else:
                    print("网关不可达")
                
            except Exception as e:
                print(f"Gateway check failed: {e}")
            
            # 2. 检查DNS解析
            try:
                import socket
                socket.gethostbyname("google.com")
                connectivity_result["details"]["dns_resolution"] = True
                connectivity_result["internet_dns"] = True
            except Exception as e:
                print(f"DNS resolution failed: {e}")
            
            # 3. 检查外部网络连通性 (ping)
            test_hosts = ["8.8.8.8", "1.1.1.1", "223.5.5.5"]  # Google DNS, Cloudflare DNS, 阿里DNS
            successful_pings = 0
            total_latency = 0
            
            for host in test_hosts:
                try:
                    latency = ping3.ping(host, timeout=5)
                    if latency is not None:
                        successful_pings += 1
                        total_latency += latency * 1000
                        connectivity_result["latency"][host] = latency * 1000
                except Exception as e:
                    print(f"Ping to {host} failed: {e}")
            
            if successful_pings > 0:
                connectivity_result["details"]["external_ping"] = True
                connectivity_result["latency"]["average_external"] = total_latency / successful_pings
            
            # 4. 检查HTTP连通性
            try:
                import requests
                response = requests.get("http://www.baidu.com", timeout=10)
                if response.status_code == 200:
                    connectivity_result["details"]["http_response"] = True
                    connectivity_result["internet_http"] = True
            except Exception as e:
                # 尝试其他网站
                try:
                    response = requests.get("http://www.baidu.com", timeout=10)
                    if response.status_code == 200:
                        connectivity_result["details"]["http_response"] = True
                        connectivity_result["internet_http"] = True
                except Exception as e2:
                    print(f"HTTP connectivity check failed: {e2}")
            
            # 5. 综合判断网络状态
            if connectivity_result["local_network"] and connectivity_result["internet_dns"] and connectivity_result["details"]["external_ping"]:
                connectivity_result["status"] = "excellent"
                connectivity_result["message"] = "网络连接正常，所有测试通过"
            elif connectivity_result["local_network"] and connectivity_result["details"]["external_ping"]:
                connectivity_result["status"] = "good"
                connectivity_result["message"] = "网络连接良好，但DNS解析可能有问题"
            elif connectivity_result["local_network"]:
                connectivity_result["status"] = "limited"
                connectivity_result["message"] = "本地网络正常，但无法访问互联网"
            else:
                connectivity_result["status"] = "disconnected"
                connectivity_result["message"] = "网络连接异常，请检查网络设置"
            
            return connectivity_result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"网络检测失败: {str(e)}",
                "timestamp": int(time.time())
            } 