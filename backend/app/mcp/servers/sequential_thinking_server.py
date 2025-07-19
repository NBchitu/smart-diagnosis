"""
Sequential Thinking MCP服务器
用于网络故障诊断的智能排障思路整理
"""

import asyncio
import json
import sys
from typing import Dict, List, Optional, Any
import logging
from fastmcp import FastMCP
from datetime import datetime

# 创建MCP应用
mcp = FastMCP("Sequential Thinking Server")

logger = logging.getLogger(__name__)

@mcp.tool()
async def analyze_network_problem(
    problem_description: str,
    symptoms: List[str] = None,
    environment_info: Dict[str, Any] = None,
    priority: str = "medium"
) -> Dict:
    """
    分析网络问题并生成排障思路
    
    Args:
        problem_description: 问题描述
        symptoms: 症状列表
        environment_info: 环境信息
        priority: 优先级 (low, medium, high, critical)
    
    Returns:
        包含排障思路的字典
    """
    try:
        # 标准化输入
        symptoms = symptoms or []
        environment_info = environment_info or {}
        
        # 分析问题类型
        problem_type = _classify_problem_type(problem_description, symptoms)
        
        # 生成排障思路
        troubleshooting_steps = _generate_troubleshooting_steps(
            problem_type, problem_description, symptoms, environment_info
        )
        
        # 评估影响程度
        impact_assessment = _assess_impact(problem_description, symptoms, priority)
        
        # 预估解决时间
        estimated_resolution_time = _estimate_resolution_time(problem_type, priority)
        
        # 推荐诊断工具
        recommended_tools = _recommend_diagnostic_tools(problem_type)
        
        result = {
            "success": True,
            "analysis": {
                "problem_type": problem_type,
                "priority": priority,
                "impact_assessment": impact_assessment,
                "estimated_resolution_time": estimated_resolution_time,
                "troubleshooting_steps": troubleshooting_steps,
                "recommended_tools": recommended_tools,
                "key_focus_areas": _identify_key_focus_areas(problem_type, symptoms)
            },
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "confidence_score": _calculate_confidence_score(problem_type, symptoms),
                "complexity_level": _assess_complexity(problem_type, symptoms)
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"问题分析失败: {str(e)}")
        return {
            "success": False,
            "error": f"分析异常: {str(e)}",
            "problem_description": problem_description
        }

@mcp.tool()
async def generate_diagnostic_sequence(
    problem_type: str,
    available_tools: List[str] = None,
    time_constraint: int = 30
) -> Dict:
    """
    生成诊断序列
    
    Args:
        problem_type: 问题类型
        available_tools: 可用工具列表
        time_constraint: 时间限制（分钟）
    
    Returns:
        包含诊断序列的字典
    """
    try:
        available_tools = available_tools or []
        
        # 生成基础诊断序列
        diagnostic_sequence = _create_diagnostic_sequence(problem_type, available_tools)
        
        # 根据时间限制调整序列
        if time_constraint < 15:
            diagnostic_sequence = _create_quick_diagnostic_sequence(problem_type)
        elif time_constraint > 60:
            diagnostic_sequence = _create_comprehensive_diagnostic_sequence(problem_type)
        
        # 评估每个步骤的重要性
        for step in diagnostic_sequence:
            step["importance"] = _assess_step_importance(step, problem_type)
            step["estimated_duration"] = _estimate_step_duration(step)
        
        return {
            "success": True,
            "diagnostic_sequence": diagnostic_sequence,
            "total_steps": len(diagnostic_sequence),
            "estimated_total_time": sum(step["estimated_duration"] for step in diagnostic_sequence),
            "critical_steps": [step for step in diagnostic_sequence if step["importance"] == "critical"]
        }
        
    except Exception as e:
        logger.error(f"诊断序列生成失败: {str(e)}")
        return {
            "success": False,
            "error": f"序列生成异常: {str(e)}",
            "problem_type": problem_type
        }

@mcp.tool()
async def evaluate_diagnostic_results(
    diagnostic_results: Dict[str, Any],
    original_problem: str,
    expected_outcomes: List[str] = None
) -> Dict:
    """
    评估诊断结果
    
    Args:
        diagnostic_results: 诊断结果数据
        original_problem: 原始问题描述
        expected_outcomes: 期望结果列表
    
    Returns:
        包含评估结果的字典
    """
    try:
        expected_outcomes = expected_outcomes or []
        
        # 分析诊断结果
        analysis = _analyze_diagnostic_results(diagnostic_results)
        
        # 识别问题根因
        root_cause = _identify_root_cause(analysis, original_problem)
        
        # 生成解决方案
        solutions = _generate_solutions(root_cause, analysis)
        
        # 评估解决方案可行性
        solution_feasibility = _evaluate_solution_feasibility(solutions)
        
        # 生成下一步行动建议
        next_actions = _generate_next_actions(root_cause, solutions)
        
        return {
            "success": True,
            "evaluation": {
                "root_cause": root_cause,
                "confidence_level": analysis.get("confidence_level", "medium"),
                "solutions": solutions,
                "solution_feasibility": solution_feasibility,
                "next_actions": next_actions,
                "resolution_likelihood": _calculate_resolution_likelihood(analysis)
            },
            "summary": {
                "key_findings": analysis.get("key_findings", []),
                "critical_issues": analysis.get("critical_issues", []),
                "recommended_priority": _recommend_priority(analysis)
            }
        }
        
    except Exception as e:
        logger.error(f"结果评估失败: {str(e)}")
        return {
            "success": False,
            "error": f"评估异常: {str(e)}",
            "original_problem": original_problem
        }

def _classify_problem_type(description: str, symptoms: List[str]) -> str:
    """分类问题类型"""
    desc_lower = description.lower()
    symptoms_text = " ".join(symptoms).lower()
    combined_text = f"{desc_lower} {symptoms_text}"
    
    # 连接性问题
    if any(keyword in combined_text for keyword in [
        "连不上", "断网", "无法连接", "timeout", "连接超时", "无网络"
    ]):
        return "connectivity"
    
    # 速度问题
    if any(keyword in combined_text for keyword in [
        "慢", "卡", "网速", "带宽", "下载", "上传", "延迟"
    ]):
        return "performance"
    
    # WiFi问题
    if any(keyword in combined_text for keyword in [
        "wifi", "无线", "信号", "干扰", "掉线", "ssid"
    ]):
        return "wifi"
    
    # DNS问题
    if any(keyword in combined_text for keyword in [
        "dns", "域名", "解析", "访问网站", "打不开"
    ]):
        return "dns"
    
    # 路由问题
    if any(keyword in combined_text for keyword in [
        "路由", "网关", "gateway", "ping", "traceroute"
    ]):
        return "routing"
    
    # 硬件问题
    if any(keyword in combined_text for keyword in [
        "网卡", "硬件", "驱动", "设备", "接口"
    ]):
        return "hardware"
    
    return "general"

def _generate_troubleshooting_steps(
    problem_type: str,
    description: str,
    symptoms: List[str],
    environment_info: Dict[str, Any]
) -> List[Dict]:
    """生成排障步骤"""
    
    base_steps = [
        {
            "step": 1,
            "title": "问题确认",
            "description": "确认问题现象和影响范围",
            "action": "收集详细的问题描述和症状信息",
            "expected_outcome": "明确问题的具体表现",
            "tools_needed": [],
            "estimated_time": 5
        }
    ]
    
    if problem_type == "connectivity":
        base_steps.extend([
            {
                "step": 2,
                "title": "基础连通性测试",
                "description": "测试到网关和外网的连通性",
                "action": "执行ping测试到默认网关和公共DNS",
                "expected_outcome": "确定网络连通性状态",
                "tools_needed": ["ping", "traceroute"],
                "estimated_time": 10
            },
            {
                "step": 3,
                "title": "网络配置检查",
                "description": "检查IP配置和路由表",
                "action": "查看网络接口配置和路由信息",
                "expected_outcome": "确认网络配置正确性",
                "tools_needed": ["ifconfig", "route"],
                "estimated_time": 8
            }
        ])
    
    elif problem_type == "performance":
        base_steps.extend([
            {
                "step": 2,
                "title": "带宽测试",
                "description": "测试网络带宽和延迟",
                "action": "执行网络速度测试",
                "expected_outcome": "获取当前网络性能指标",
                "tools_needed": ["speedtest", "ping"],
                "estimated_time": 15
            },
            {
                "step": 3,
                "title": "流量分析",
                "description": "分析网络流量模式",
                "action": "监控网络流量并分析带宽使用情况",
                "expected_outcome": "识别流量瓶颈",
                "tools_needed": ["netstat", "iftop"],
                "estimated_time": 20
            }
        ])
    
    elif problem_type == "wifi":
        base_steps.extend([
            {
                "step": 2,
                "title": "WiFi信号检测",
                "description": "扫描WiFi信号并检测干扰",
                "action": "扫描周围WiFi网络并分析信号强度",
                "expected_outcome": "评估WiFi信号质量和干扰情况",
                "tools_needed": ["iwlist", "iwconfig"],
                "estimated_time": 10
            },
            {
                "step": 3,
                "title": "信道分析",
                "description": "分析WiFi信道使用情况",
                "action": "检查信道拥塞和推荐最佳信道",
                "expected_outcome": "识别最佳WiFi信道",
                "tools_needed": ["wifi_analyzer"],
                "estimated_time": 12
            }
        ])
    
    elif problem_type == "dns":
        base_steps.extend([
            {
                "step": 2,
                "title": "DNS解析测试",
                "description": "测试DNS解析功能",
                "action": "使用不同DNS服务器测试域名解析",
                "expected_outcome": "确定DNS解析状态",
                "tools_needed": ["nslookup", "dig"],
                "estimated_time": 8
            },
            {
                "step": 3,
                "title": "DNS配置检查",
                "description": "检查DNS配置和缓存",
                "action": "验证DNS配置并清除缓存",
                "expected_outcome": "确保DNS配置正确",
                "tools_needed": ["resolv.conf"],
                "estimated_time": 5
            }
        ])
    
    # 添加通用结束步骤
    base_steps.append({
        "step": len(base_steps) + 1,
        "title": "解决方案实施",
        "description": "根据诊断结果实施解决方案",
        "action": "应用识别的解决方案并验证效果",
        "expected_outcome": "问题得到解决",
        "tools_needed": [],
        "estimated_time": 15
    })
    
    return base_steps

def _assess_impact(description: str, symptoms: List[str], priority: str) -> Dict:
    """评估影响程度"""
    desc_lower = description.lower()
    symptoms_text = " ".join(symptoms).lower()
    
    # 业务影响评估
    business_impact = "low"
    if any(keyword in desc_lower for keyword in ["无法工作", "业务中断", "客户"]):
        business_impact = "high"
    elif any(keyword in desc_lower for keyword in ["影响", "缓慢", "不稳定"]):
        business_impact = "medium"
    
    # 用户影响评估
    user_impact = "low"
    if "多人" in desc_lower or "所有人" in desc_lower:
        user_impact = "high"
    elif "部分" in desc_lower or "个别" in desc_lower:
        user_impact = "medium"
    
    # 系统影响评估
    system_impact = "low"
    if any(keyword in desc_lower for keyword in ["服务器", "系统", "网络中断"]):
        system_impact = "high"
    elif any(keyword in desc_lower for keyword in ["应用", "服务"]):
        system_impact = "medium"
    
    return {
        "overall_impact": _calculate_overall_impact(business_impact, user_impact, system_impact),
        "business_impact": business_impact,
        "user_impact": user_impact,
        "system_impact": system_impact,
        "urgency": _calculate_urgency(priority, business_impact)
    }

def _estimate_resolution_time(problem_type: str, priority: str) -> Dict:
    """预估解决时间"""
    base_times = {
        "connectivity": 30,
        "performance": 45,
        "wifi": 20,
        "dns": 15,
        "routing": 40,
        "hardware": 60,
        "general": 35
    }
    
    base_time = base_times.get(problem_type, 30)
    
    # 根据优先级调整
    priority_multipliers = {
        "critical": 0.7,  # 紧急情况下投入更多资源
        "high": 0.8,
        "medium": 1.0,
        "low": 1.2
    }
    
    estimated_time = base_time * priority_multipliers.get(priority, 1.0)
    
    return {
        "estimated_minutes": int(estimated_time),
        "range": {
            "min": int(estimated_time * 0.7),
            "max": int(estimated_time * 1.5)
        },
        "confidence": "medium"
    }

def _recommend_diagnostic_tools(problem_type: str) -> List[Dict]:
    """推荐诊断工具"""
    tool_mapping = {
        "connectivity": [
            {"name": "ping", "priority": "high", "description": "测试网络连通性"},
            {"name": "traceroute", "priority": "high", "description": "追踪网络路径"},
            {"name": "netstat", "priority": "medium", "description": "显示网络连接状态"}
        ],
        "performance": [
            {"name": "speedtest", "priority": "high", "description": "测试网络速度"},
            {"name": "iperf", "priority": "medium", "description": "测试带宽性能"},
            {"name": "ntopng", "priority": "low", "description": "流量监控"}
        ],
        "wifi": [
            {"name": "iwlist", "priority": "high", "description": "WiFi网络扫描"},
            {"name": "iwconfig", "priority": "high", "description": "WiFi配置查看"},
            {"name": "wifi_analyzer", "priority": "medium", "description": "WiFi信号分析"}
        ],
        "dns": [
            {"name": "nslookup", "priority": "high", "description": "DNS查询工具"},
            {"name": "dig", "priority": "high", "description": "DNS诊断工具"},
            {"name": "host", "priority": "medium", "description": "DNS主机查询"}
        ]
    }
    
    return tool_mapping.get(problem_type, [
        {"name": "ping", "priority": "medium", "description": "基础连通性测试"},
        {"name": "netstat", "priority": "medium", "description": "网络状态查看"}
    ])

def _identify_key_focus_areas(problem_type: str, symptoms: List[str]) -> List[str]:
    """识别关键关注领域"""
    focus_areas = []
    
    if problem_type == "connectivity":
        focus_areas = ["网络连通性", "路由配置", "防火墙设置", "物理连接"]
    elif problem_type == "performance":
        focus_areas = ["带宽利用率", "网络延迟", "QoS配置", "硬件性能"]
    elif problem_type == "wifi":
        focus_areas = ["信号强度", "信道干扰", "WiFi配置", "设备兼容性"]
    elif problem_type == "dns":
        focus_areas = ["DNS服务器", "域名解析", "缓存策略", "网络配置"]
    else:
        focus_areas = ["基础连通性", "网络配置", "硬件状态", "服务状态"]
    
    return focus_areas

def _calculate_confidence_score(problem_type: str, symptoms: List[str]) -> float:
    """计算置信度分数"""
    base_confidence = 0.7
    
    # 根据症状数量调整
    if len(symptoms) >= 3:
        base_confidence += 0.15
    elif len(symptoms) >= 2:
        base_confidence += 0.1
    
    # 根据问题类型调整
    if problem_type in ["connectivity", "dns", "wifi"]:
        base_confidence += 0.1
    
    return min(base_confidence, 1.0)

def _assess_complexity(problem_type: str, symptoms: List[str]) -> str:
    """评估复杂程度"""
    complexity_score = 0
    
    # 根据问题类型评分
    type_scores = {
        "dns": 1,
        "wifi": 2,
        "connectivity": 2,
        "performance": 3,
        "routing": 4,
        "hardware": 4,
        "general": 3
    }
    
    complexity_score += type_scores.get(problem_type, 2)
    
    # 根据症状数量调整
    if len(symptoms) > 3:
        complexity_score += 2
    elif len(symptoms) > 1:
        complexity_score += 1
    
    if complexity_score <= 2:
        return "low"
    elif complexity_score <= 4:
        return "medium"
    else:
        return "high"

def _create_diagnostic_sequence(problem_type: str, available_tools: List[str]) -> List[Dict]:
    """创建诊断序列"""
    # 基础诊断序列模板
    sequences = {
        "connectivity": [
            {"name": "ping_gateway", "description": "测试网关连通性", "tool": "ping", "critical": True},
            {"name": "ping_dns", "description": "测试DNS服务器", "tool": "ping", "critical": True},
            {"name": "trace_route", "description": "追踪网络路径", "tool": "traceroute", "critical": False}
        ],
        "performance": [
            {"name": "speed_test", "description": "网络速度测试", "tool": "speedtest", "critical": True},
            {"name": "latency_test", "description": "网络延迟测试", "tool": "ping", "critical": True},
            {"name": "bandwidth_analysis", "description": "带宽分析", "tool": "iperf", "critical": False}
        ],
        "wifi": [
            {"name": "wifi_scan", "description": "WiFi网络扫描", "tool": "iwlist", "critical": True},
            {"name": "signal_strength", "description": "信号强度检测", "tool": "iwconfig", "critical": True},
            {"name": "interference_check", "description": "干扰检测", "tool": "wifi_analyzer", "critical": False}
        ]
    }
    
    return sequences.get(problem_type, [
        {"name": "basic_ping", "description": "基础连通性测试", "tool": "ping", "critical": True}
    ])

def _create_quick_diagnostic_sequence(problem_type: str) -> List[Dict]:
    """创建快速诊断序列"""
    quick_sequences = {
        "connectivity": [
            {"name": "quick_ping", "description": "快速ping测试", "tool": "ping", "critical": True}
        ],
        "performance": [
            {"name": "quick_speed", "description": "快速速度测试", "tool": "speedtest", "critical": True}
        ],
        "wifi": [
            {"name": "quick_wifi", "description": "快速WiFi检测", "tool": "iwconfig", "critical": True}
        ]
    }
    
    return quick_sequences.get(problem_type, [
        {"name": "basic_check", "description": "基础检查", "tool": "ping", "critical": True}
    ])

def _create_comprehensive_diagnostic_sequence(problem_type: str) -> List[Dict]:
    """创建综合诊断序列"""
    # 详细的诊断序列
    return _create_diagnostic_sequence(problem_type, []) + [
        {"name": "detailed_analysis", "description": "详细分析", "tool": "analysis", "critical": False},
        {"name": "performance_monitoring", "description": "性能监控", "tool": "monitor", "critical": False}
    ]

def _assess_step_importance(step: Dict, problem_type: str) -> str:
    """评估步骤重要性"""
    if step.get("critical", False):
        return "critical"
    elif step.get("tool") in ["ping", "speedtest", "iwconfig"]:
        return "high"
    else:
        return "medium"

def _estimate_step_duration(step: Dict) -> int:
    """估算步骤持续时间"""
    duration_map = {
        "ping": 5,
        "speedtest": 15,
        "traceroute": 10,
        "iwlist": 8,
        "iwconfig": 3,
        "analysis": 20
    }
    
    return duration_map.get(step.get("tool"), 5)

def _analyze_diagnostic_results(results: Dict[str, Any]) -> Dict:
    """分析诊断结果"""
    analysis = {
        "key_findings": [],
        "critical_issues": [],
        "confidence_level": "medium"
    }
    
    # 简化的分析逻辑
    if "ping" in results:
        ping_data = results["ping"]
        if not ping_data.get("success", False):
            analysis["critical_issues"].append("网络连通性异常")
            analysis["key_findings"].append("ping测试失败")
    
    if "speedtest" in results:
        speed_data = results["speedtest"]
        if speed_data.get("download_speed", 0) < 10:
            analysis["critical_issues"].append("网络速度过慢")
            analysis["key_findings"].append("下载速度低于预期")
    
    return analysis

def _identify_root_cause(analysis: Dict, problem: str) -> Dict:
    """识别根本原因"""
    root_cause = {
        "primary_cause": "unknown",
        "contributing_factors": [],
        "confidence": "medium"
    }
    
    # 基于分析结果识别根因
    if "网络连通性异常" in analysis.get("critical_issues", []):
        root_cause["primary_cause"] = "connectivity_failure"
        root_cause["contributing_factors"] = ["网络配置错误", "硬件故障", "运营商问题"]
    
    elif "网络速度过慢" in analysis.get("critical_issues", []):
        root_cause["primary_cause"] = "performance_degradation"
        root_cause["contributing_factors"] = ["带宽不足", "网络拥塞", "设备性能"]
    
    return root_cause

def _generate_solutions(root_cause: Dict, analysis: Dict) -> List[Dict]:
    """生成解决方案"""
    solutions = []
    
    primary_cause = root_cause.get("primary_cause", "unknown")
    
    if primary_cause == "connectivity_failure":
        solutions = [
            {"solution": "检查网络配置", "priority": "high", "effort": "low"},
            {"solution": "重启网络设备", "priority": "high", "effort": "low"},
            {"solution": "联系运营商", "priority": "medium", "effort": "medium"}
        ]
    
    elif primary_cause == "performance_degradation":
        solutions = [
            {"solution": "优化QoS配置", "priority": "high", "effort": "medium"},
            {"solution": "升级带宽", "priority": "medium", "effort": "high"},
            {"solution": "优化网络拓扑", "priority": "low", "effort": "high"}
        ]
    
    return solutions

def _evaluate_solution_feasibility(solutions: List[Dict]) -> Dict:
    """评估解决方案可行性"""
    feasibility = {
        "high_feasibility": [],
        "medium_feasibility": [],
        "low_feasibility": []
    }
    
    for solution in solutions:
        effort = solution.get("effort", "medium")
        priority = solution.get("priority", "medium")
        
        if effort == "low" and priority == "high":
            feasibility["high_feasibility"].append(solution)
        elif effort == "medium":
            feasibility["medium_feasibility"].append(solution)
        else:
            feasibility["low_feasibility"].append(solution)
    
    return feasibility

def _generate_next_actions(root_cause: Dict, solutions: List[Dict]) -> List[Dict]:
    """生成下一步行动"""
    next_actions = []
    
    # 基于根因和解决方案生成行动项
    for solution in solutions:
        if solution.get("priority") == "high":
            next_actions.append({
                "action": solution["solution"],
                "timeline": "immediate",
                "owner": "network_admin",
                "dependencies": []
            })
    
    return next_actions

def _calculate_resolution_likelihood(analysis: Dict) -> float:
    """计算解决可能性"""
    base_likelihood = 0.7
    
    # 根据关键问题数量调整
    critical_issues = len(analysis.get("critical_issues", []))
    if critical_issues == 0:
        base_likelihood = 0.9
    elif critical_issues > 2:
        base_likelihood = 0.5
    
    return base_likelihood

def _recommend_priority(analysis: Dict) -> str:
    """推荐优先级"""
    critical_issues = len(analysis.get("critical_issues", []))
    
    if critical_issues >= 2:
        return "critical"
    elif critical_issues == 1:
        return "high"
    else:
        return "medium"

def _calculate_overall_impact(business: str, user: str, system: str) -> str:
    """计算总体影响"""
    impact_weights = {"high": 3, "medium": 2, "low": 1}
    
    total_score = (
        impact_weights[business] * 0.4 +
        impact_weights[user] * 0.3 +
        impact_weights[system] * 0.3
    )
    
    if total_score >= 2.5:
        return "high"
    elif total_score >= 1.5:
        return "medium"
    else:
        return "low"

def _calculate_urgency(priority: str, business_impact: str) -> str:
    """计算紧急程度"""
    if priority == "critical" or business_impact == "high":
        return "urgent"
    elif priority == "high" or business_impact == "medium":
        return "high"
    else:
        return "normal"

def main():
    """运行MCP服务器"""
    import asyncio
    
    # 创建新的事件循环并运行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(mcp.run())
    finally:
        loop.close()

if __name__ == "__main__":
    main()