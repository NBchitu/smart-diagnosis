"""
MCP管理器 - 统一管理MCP客户端和服务器
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import os
from pathlib import Path

from .client import MCPClient, MCPResponse
from .config import MCPConfig

logger = logging.getLogger(__name__)

class MCPManager:
    """MCP管理器类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.client: Optional[MCPClient] = None
            self.config: Optional[MCPConfig] = None
            self._tools_registry = {}
            self._server_capabilities = {}
            MCPManager._initialized = True
    
    async def initialize(self, config_path: Optional[str] = None):
        """初始化MCP管理器"""
        try:
            # 设置默认配置路径
            if config_path is None:
                config_path = os.path.join(
                    os.path.dirname(__file__), "..", "..", "..", "config", "mcp_config.json"
                )
            
            # 加载配置
            self.config = MCPConfig.load_from_file(config_path)
            logger.info(f"MCP配置已加载: {config_path}")
            
            # 创建并初始化客户端
            self.client = MCPClient(self.config)
            await self.client.initialize()
            
            # 注册工具能力
            await self._register_tools()
            
            logger.info("MCP管理器初始化完成")
            
        except Exception as e:
            logger.error(f"MCP管理器初始化失败: {str(e)}")
            raise
    
    async def _register_tools(self):
        """注册所有可用工具"""
        try:
            # 定义每个服务器的工具能力
            self._tools_registry = {
                "ping": {
                    "ping_host": {
                        "description": "Ping指定主机检测网络连通性",
                        "parameters": {
                            "host": {"type": "string", "required": True},
                            "count": {"type": "integer", "default": 4},
                            "timeout": {"type": "integer", "default": 10},
                            "packet_size": {"type": "integer", "default": 32}
                        }
                    },
                    "ping_multiple_hosts": {
                        "description": "同时Ping多个主机",
                        "parameters": {
                            "hosts": {"type": "array", "required": True},
                            "count": {"type": "integer", "default": 4},
                            "timeout": {"type": "integer", "default": 10}
                        }
                    },
                    "traceroute_host": {
                        "description": "路由跟踪到指定主机",
                        "parameters": {
                            "host": {"type": "string", "required": True},
                            "max_hops": {"type": "integer", "default": 30},
                            "timeout": {"type": "integer", "default": 5}
                        }
                    }
                },
                "wifi": {
                    "scan_wifi_networks": {
                        "description": "扫描周围的WiFi网络",
                        "parameters": {}
                    },
                    "get_current_wifi_info": {
                        "description": "获取当前连接的WiFi信息",
                        "parameters": {}
                    },
                    "analyze_wifi_interference": {
                        "description": "分析WiFi干扰情况",
                        "parameters": {
                            "interface": {"type": "string", "default": "wlan0"},
                            "duration": {"type": "integer", "default": 30}
                        }
                    },
                    "get_wifi_channel_utilization": {
                        "description": "获取WiFi信道利用率",
                        "parameters": {}
                    },
                    "measure_signal_strength": {
                        "description": "测量WiFi信号强度",
                        "parameters": {
                            "target_ssid": {"type": "string", "optional": True},
                            "duration": {"type": "integer", "default": 10}
                        }
                    }
                },
                "packet_capture": {
                    "start_packet_capture": {
                        "description": "开始智能网络抓包，根据抓包模式自动选择合适的过滤器",
                        "parameters": {
                            "target": {"type": "string", "required": True, "description": "抓包目标：域名、IP地址或端口号"},
                            "mode": {"type": "string", "default": "auto", "description": "抓包模式：domain、port、web、diagnosis、auto"},
                            "duration": {"type": "integer", "default": 30, "description": "抓包持续时间（秒）"},
                            "interface": {"type": "string", "optional": True, "description": "网络接口，留空自动检测"}
                        }
                    },
                    "stop_packet_capture": {
                        "description": "停止当前的抓包任务",
                        "parameters": {}
                    },
                    "get_capture_status": {
                        "description": "获取当前抓包状态和已分析的数据包信息",
                        "parameters": {}
                    },
                    "list_network_interfaces": {
                        "description": "列出所有可用的网络接口",
                        "parameters": {}
                    }
                },
                "gateway": {
                    "get_default_gateway": {
                        "description": "获取默认网关信息",
                        "parameters": {}
                    },
                    "get_all_gateways": {
                        "description": "获取所有网关信息",
                        "parameters": {}
                    },
                    "probe_gateway": {
                        "description": "探测网关信息",
                        "parameters": {
                            "gateway_ip": {"type": "string", "required": True},
                            "detailed": {"type": "boolean", "default": True}
                        }
                    },
                    "analyze_gateway_performance": {
                        "description": "分析网关性能",
                        "parameters": {
                            "gateway_ip": {"type": "string", "optional": True},
                            "test_duration": {"type": "integer", "default": 60},
                            "test_interval": {"type": "integer", "default": 5}
                        }
                    },
                    "check_gateway_services": {
                        "description": "检查网关服务",
                        "parameters": {
                            "gateway_ip": {"type": "string", "required": True}
                        }
                    }
                },
                "connectivity": {
                    "check_internet_connectivity": {
                        "description": "检查互联网连通性",
                        "parameters": {
                            "test_hosts": {"type": "array", "optional": True},
                            "timeout": {"type": "integer", "default": 10}
                        }
                    },
                    "check_dns_resolution": {
                        "description": "检查DNS解析",
                        "parameters": {
                            "domains": {"type": "array", "optional": True},
                            "dns_servers": {"type": "array", "optional": True}
                        }
                    },
                    "check_port_connectivity": {
                        "description": "检查端口连通性",
                        "parameters": {
                            "host": {"type": "string", "required": True},
                            "ports": {"type": "array", "required": True},
                            "timeout": {"type": "integer", "default": 5}
                        }
                    },
                    "bandwidth_test": {
                        "description": "网络带宽测试",
                        "parameters": {
                            "test_duration": {"type": "integer", "default": 30},
                            "server_url": {"type": "string", "optional": True}
                        }
                    },
                    "comprehensive_connectivity_test": {
                        "description": "综合连通性测试",
                        "parameters": {
                            "quick_test": {"type": "boolean", "default": False}
                        }
                    }
                },
                "sequential_thinking": {
                    "analyze_network_problem": {
                        "description": "分析网络问题并生成排障思路",
                        "parameters": {
                            "problem_description": {"type": "string", "required": True},
                            "symptoms": {"type": "array", "optional": True},
                            "environment_info": {"type": "object", "optional": True},
                            "priority": {"type": "string", "default": "medium"}
                        }
                    },
                    "generate_diagnostic_sequence": {
                        "description": "生成诊断序列",
                        "parameters": {
                            "problem_type": {"type": "string", "required": True},
                            "available_tools": {"type": "array", "optional": True},
                            "time_constraint": {"type": "integer", "default": 30}
                        }
                    },
                    "evaluate_diagnostic_results": {
                        "description": "评估诊断结果",
                        "parameters": {
                            "diagnostic_results": {"type": "object", "required": True},
                            "original_problem": {"type": "string", "required": True},
                            "expected_outcomes": {"type": "array", "optional": True}
                        }
                    }
                }
            }
            
            logger.info(f"工具注册表已建立，共 {len(self._tools_registry)} 个服务器")
            
        except Exception as e:
            logger.error(f"工具注册失败: {str(e)}")
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        args: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> MCPResponse:
        """调用指定工具"""
        if not self.client:
            raise RuntimeError("MCP管理器未初始化")
        print("call_tool被调用")
        print(f"server_name: {server_name}")
        print(f"tool_name: {tool_name}")
        print(f"args: {args}")
        print(f"timeout: {timeout}")
        return await self.client.call_tool(server_name, tool_name, args, timeout)
    
    async def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用工具"""
        available_tools = {}
        
        # 检查每个服务器的状态
        if self.client:
            server_status = await self.client.list_servers()
            
            for server_name, tools in self._tools_registry.items():
                if server_name in server_status:
                    status = server_status[server_name]["status"]
                    if status.get("status") == "running":
                        available_tools[server_name] = tools
        
        return available_tools
    
    async def diagnose_network_issue(self, issue_description: str) -> Dict[str, Any]:
        """智能网络问题诊断"""
        try:
            logger.info(f"开始网络问题诊断: {issue_description}")
            
            # 基于问题描述选择诊断步骤
            diagnosis_plan = self._create_diagnosis_plan(issue_description)
            
            # 执行诊断步骤
            results = {}
            for step in diagnosis_plan:
                step_name = step["name"]
                server = step["server"]
                tool = step["tool"]
                args = step["args"]
                
                logger.info(f"执行诊断步骤: {step_name}")
                
                response = await self.call_tool(server, tool, args)
                results[step_name] = {
                    "success": response.success,
                    "data": response.data,
                    "error": response.error,
                    "execution_time": response.execution_time
                }
                
                # 如果关键步骤失败，调整后续步骤
                if not response.success and step.get("critical", False):
                    logger.warning(f"关键诊断步骤失败: {step_name}")
                    break
            
            # 分析诊断结果
            analysis = self._analyze_diagnosis_results(results, issue_description)
            
            return {
                "success": True,
                "issue_description": issue_description,
                "diagnosis_results": results,
                "analysis": analysis,
                "recommendations": analysis.get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"网络问题诊断失败: {str(e)}")
            return {
                "success": False,
                "error": f"诊断异常: {str(e)}",
                "issue_description": issue_description
            }
    
    def _create_diagnosis_plan(self, issue_description: str) -> List[Dict[str, Any]]:
        """根据问题描述创建诊断计划"""
        # 将问题描述转换为小写便于匹配
        issue_lower = issue_description.lower()
        
        plan = []
        
        # 基础连通性检查（总是执行）
        plan.append({
            "name": "basic_connectivity",
            "server": "connectivity",
            "tool": "check_internet_connectivity",
            "args": {},
            "critical": True
        })
        
        # DNS相关问题
        if any(keyword in issue_lower for keyword in ["dns", "解析", "域名", "无法访问网站"]):
            plan.extend([
                {
                    "name": "dns_check",
                    "server": "connectivity",
                    "tool": "check_dns_resolution",
                    "args": {}
                },
                {
                    "name": "gateway_info",
                    "server": "gateway",
                    "tool": "get_default_gateway",
                    "args": {}
                }
            ])
        
        # WiFi相关问题
        if any(keyword in issue_lower for keyword in ["wifi", "无线", "信号", "连接断开", "干扰"]):
            plan.extend([
                {
                    "name": "wifi_scan",
                    "server": "wifi",
                    "tool": "scan_wifi_networks",
                    "args": {}
                },
                {
                    "name": "current_wifi",
                    "server": "wifi",
                    "tool": "get_current_wifi_info",
                    "args": {}
                },
                {
                    "name": "wifi_interference",
                    "server": "wifi",
                    "tool": "analyze_wifi_interference",
                    "args": {"duration": 30}
                },
                {
                    "name": "signal_strength",
                    "server": "wifi",
                    "tool": "measure_signal_strength",
                    "args": {"duration": 10}
                }
            ])
        
        # 速度/带宽问题
        if any(keyword in issue_lower for keyword in ["慢", "卡", "带宽", "速度", "下载"]):
            plan.extend([
                {
                    "name": "bandwidth_test",
                    "server": "connectivity",
                    "tool": "bandwidth_test",
                    "args": {"test_duration": 20}
                },
                {
                    "name": "traffic_analysis",
                    "server": "packet_capture",
                    "tool": "start_packet_capture",
                    "args": {"target": "auto", "mode": "diagnosis", "duration": 30}
                }
            ])
        
        # 连通性问题
        if any(keyword in issue_lower for keyword in ["ping", "延迟", "丢包", "超时"]):
            plan.extend([
                {
                    "name": "ping_test",
                    "server": "ping",
                    "tool": "ping_multiple_hosts",
                    "args": {
                        "hosts": ["8.8.8.8", "1.1.1.1", "baidu.com"],
                        "count": 5
                    }
                },
                {
                    "name": "gateway_performance",
                    "server": "gateway",
                    "tool": "analyze_gateway_performance",
                    "args": {"test_duration": 30}
                }
            ])
        
        # 如果是复杂问题，执行综合测试
        if len(plan) <= 2:  # 只有基础检查
            plan.append({
                "name": "comprehensive_test",
                "server": "connectivity",
                "tool": "comprehensive_connectivity_test",
                "args": {"quick_test": True}
            })
        
        return plan
    
    def _analyze_diagnosis_results(
        self,
        results: Dict[str, Any],
        issue_description: str
    ) -> Dict[str, Any]:
        """分析诊断结果"""
        analysis = {
            "summary": "",
            "issues_found": [],
            "recommendations": [],
            "severity": "unknown"
        }
        
        try:
            issues_found = []
            recommendations = []
            
            # 分析基础连通性
            basic_conn = results.get("basic_connectivity", {})
            if basic_conn.get("success") and basic_conn.get("data"):
                connectivity_score = basic_conn["data"].get("connectivity_score", 0)
                if connectivity_score < 50:
                    issues_found.append("互联网连通性严重异常")
                    recommendations.append("检查网络物理连接和路由器状态")
                elif connectivity_score < 80:
                    issues_found.append("互联网连通性不稳定")
                    recommendations.append("检查网络配置，可能存在DNS或路由问题")
            
            # 分析DNS问题
            dns_check = results.get("dns_check", {})
            if dns_check.get("success") and dns_check.get("data"):
                dns_analysis = dns_check["data"].get("analysis", {})
                if dns_analysis.get("avg_success_rate", 100) < 70:
                    issues_found.append("DNS解析异常")
                    best_dns = dns_analysis.get("best_dns_server")
                    if best_dns:
                        recommendations.append(f"建议使用DNS服务器: {best_dns}")
            
            # 分析WiFi问题
            wifi_info = results.get("current_wifi", {})
            if wifi_info.get("success") and wifi_info.get("data"):
                wifi_data = wifi_info["data"].get("wifi_info", {})
                if wifi_data.get("connected"):
                    signal_level = wifi_data.get("signal_level", 0)
                    if signal_level < -70:  # 信号弱
                        issues_found.append("WiFi信号强度较弱")
                        recommendations.append("移动设备靠近路由器或调整路由器位置")
                else:
                    issues_found.append("未连接到WiFi网络")
                    recommendations.append("检查WiFi连接状态和密码")
            
            # 分析带宽问题
            bandwidth_test = results.get("bandwidth_test", {})
            if bandwidth_test.get("success") and bandwidth_test.get("data"):
                bandwidth_data = bandwidth_test["data"]
                download_speed = bandwidth_data.get("download_speed", 0)
                ping_value = bandwidth_data.get("ping", 0)
                
                if download_speed < 10:  # 小于10Mbps
                    issues_found.append("下载速度过慢")
                    recommendations.append("联系运营商检查网络套餐和线路质量")
                
                if ping_value > 100:  # 延迟大于100ms
                    issues_found.append("网络延迟过高")
                    recommendations.append("检查网络拥塞情况和路由器性能")
            
            # 分析Ping测试
            ping_test = results.get("ping_test", {})
            if ping_test.get("success") and ping_test.get("data"):
                ping_data = ping_test["data"]
                failed_pings = ping_data.get("failed_pings", 0)
                total_tests = ping_data.get("total_hosts", 1)
                
                if failed_pings > total_tests * 0.5:  # 超过50%失败
                    issues_found.append("网络连通性严重异常")
                    recommendations.append("检查防火墙设置和网络路由")
            
            # 确定严重程度
            if len(issues_found) == 0:
                analysis["severity"] = "normal"
                analysis["summary"] = "网络状况正常，未发现明显问题"
            elif any("严重" in issue for issue in issues_found):
                analysis["severity"] = "critical"
                analysis["summary"] = "发现严重网络问题，需要立即处理"
            elif len(issues_found) >= 3:
                analysis["severity"] = "high"
                analysis["summary"] = "发现多个网络问题，建议尽快处理"
            else:
                analysis["severity"] = "medium"
                analysis["summary"] = "发现一些网络问题，建议进行优化"
            
            analysis["issues_found"] = issues_found
            analysis["recommendations"] = recommendations
            
            # 如果没有具体建议，给出通用建议
            if not recommendations:
                recommendations.extend([
                    "重启路由器和网络设备",
                    "检查网线连接是否牢固",
                    "更新网络驱动程序",
                    "联系网络服务提供商技术支持"
                ])
                analysis["recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"诊断结果分析失败: {str(e)}")
            analysis["summary"] = "诊断结果分析异常"
            analysis["recommendations"] = ["请手动检查网络状况"]
        
        return analysis
    
    async def get_server_status(self) -> Dict[str, Any]:
        """获取所有服务器状态"""
        if not self.client:
            return {"error": "MCP客户端未初始化"}
        
        return await self.client.list_servers()
    
    async def restart_server(self, server_name: str) -> bool:
        """重启指定服务器"""
        if not self.client:
            return False
        
        return await self.client.restart_server(server_name)
    
    async def shutdown(self):
        """关闭MCP管理器"""
        if self.client:
            await self.client.shutdown()
            logger.info("MCP管理器已关闭")

# 全局MCP管理器实例
mcp_manager = MCPManager() 