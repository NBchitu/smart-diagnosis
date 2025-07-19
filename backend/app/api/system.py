from fastapi import APIRouter, HTTPException
import psutil
import platform
import subprocess
import json

router = APIRouter()

@router.get("/info")
async def get_system_info():
    """获取系统信息"""
    try:
        system_info = {
            "os": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total
        }
        
        return {
            "success": True,
            "data": system_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_system_status():
    """获取系统状态"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 尝试获取温度（树莓派）
        temperature = None
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                temperature = temp
        except:
            temperature = None
        
        status = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "temperature": temperature
        }
        
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network-interfaces")
async def get_network_interfaces():
    """获取网络接口信息"""
    try:
        interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {
                "addresses": [],
                "stats": None
            }
            
            for addr in addrs:
                interface_info["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            
            # 获取接口统计信息
            try:
                stats = psutil.net_if_stats()[interface]
                interface_info["stats"] = {
                    "isup": stats.isup,
                    "duplex": str(stats.duplex),
                    "speed": stats.speed,
                    "mtu": stats.mtu
                }
            except:
                pass
            
            interfaces[interface] = interface_info
        
        return {
            "success": True,
            "data": interfaces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gateway")
async def get_gateway_info():
    """获取网关信息"""
    try:
        print("🖥️ 后端开始获取网关信息...")
        
        gateway_info = {
            "gateway_ip": None,
            "local_ip": None,
            "network_interface": None,
            "dns_servers": [],
            "route_info": {}
        }
        
        # 方法1: 尝试使用netifaces库
        try:
            import netifaces
            gateways = netifaces.gateways()
            
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                default_gateway_info = gateways['default'][netifaces.AF_INET]
                gateway_info["gateway_ip"] = default_gateway_info[0]
                gateway_info["network_interface"] = default_gateway_info[1]
                
                # 获取本地IP
                addrs = netifaces.ifaddresses(default_gateway_info[1])
                if netifaces.AF_INET in addrs:
                    gateway_info["local_ip"] = addrs[netifaces.AF_INET][0]['addr']
                    
                print(f"✅ netifaces获取成功: {gateway_info['gateway_ip']}")
                
        except ImportError:
            print("⚠️ netifaces库未安装，尝试备用方法...")
        except Exception as e:
            print(f"⚠️ netifaces获取失败: {str(e)}，尝试备用方法...")
        
        # 方法2: 如果netifaces失败，使用ip route命令
        if not gateway_info["gateway_ip"]:
            try:
                # 使用ip route获取默认网关
                result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    print(f"📡 ip route输出: {output}")
                    
                    # 解析输出: default via 192.168.1.1 dev en0
                    parts = output.split()
                    for i, part in enumerate(parts):
                        if part == "via" and i + 1 < len(parts):
                            gateway_info["gateway_ip"] = parts[i + 1]
                        elif part == "dev" and i + 1 < len(parts):
                            gateway_info["network_interface"] = parts[i + 1]
                            
                    print(f"✅ ip route获取成功: {gateway_info['gateway_ip']}")
                    
            except Exception as e:
                print(f"⚠️ ip route失败: {str(e)}")
        
        # 方法3: 如果前面都失败，尝试route命令 (macOS)
        if not gateway_info["gateway_ip"]:
            try:
                result = subprocess.run(['route', '-n', 'get', 'default'], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    output = result.stdout
                    print(f"📡 route输出: {output}")
                    
                    # 解析route输出
                    for line in output.split('\n'):
                        if 'gateway:' in line:
                            gateway_info["gateway_ip"] = line.split('gateway:')[1].strip()
                        elif 'interface:' in line:
                            gateway_info["network_interface"] = line.split('interface:')[1].strip()
                            
                    print(f"✅ route获取成功: {gateway_info['gateway_ip']}")
                    
            except Exception as e:
                print(f"⚠️ route命令失败: {str(e)}")
        
        # 尝试获取DNS服务器信息
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns_server = line.split()[1]
                        gateway_info["dns_servers"].append(dns_server)
        except:
            # Windows或其他系统，忽略
            pass
            
        # 如果所有方法都失败，使用常见的默认值
        if not gateway_info["gateway_ip"]:
            print("⚠️ 所有方法都失败，使用默认网关地址")
            gateway_info["gateway_ip"] = "192.168.1.1"  # 常见的默认网关
            gateway_info["network_interface"] = "unknown"
            
        print(f"🎯 最终网关信息: {gateway_info}")
        
        return {
            "success": True,
            "data": gateway_info
        }
        
    except Exception as e:
        print(f"❌ 获取网关信息异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取网关信息失败: {str(e)}") 