from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import json
import asyncio

from app.mcp.manager import mcp_manager

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalysisRequest(BaseModel):
    test_results: Dict
    context: str = "network_diagnostics"

class DiagnosisRequest(BaseModel):
    issue_description: str
    user_reported_symptoms: List[str] = []
    network_environment: Optional[Dict] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[Dict] = None

@router.post("/analyze")
async def analyze_network_results(request: AnalysisRequest):
    """AI分析网络测试结果"""
    try:
        # 使用MCP工具增强分析能力
        enhanced_analysis = await _enhance_analysis_with_mcp(request.test_results)
        
        # 基础分析逻辑
        analysis = {
            "issues": [],
            "recommendations": [],
            "confidence": 0,
            "priority": "low"
        }
        
        # 集成MCP分析结果
        if enhanced_analysis.get("success"):
            mcp_data = enhanced_analysis["data"]
            analysis["issues"].extend(mcp_data.get("issues_found", []))
            analysis["recommendations"].extend(mcp_data.get("recommendations", []))
            analysis["confidence"] = _calculate_confidence(mcp_data)
            analysis["priority"] = _determine_priority(mcp_data.get("severity", "low"))
        
        # 如果没有MCP数据，使用基础分析
        if not analysis["issues"]:
            analysis = _basic_analysis(request.test_results)
        
        return {
            "success": True,
            "data": analysis,
            "mcp_enhanced": enhanced_analysis.get("success", False)
        }
    except Exception as e:
        logger.error(f"网络结果分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diagnose")
async def diagnose_network_issue(request: DiagnosisRequest):
    """智能网络问题诊断"""
    try:
        logger.info(f"开始网络问题诊断: {request.issue_description}")
        
        # 确保MCP管理器已初始化
        if not mcp_manager.client:
            await mcp_manager.initialize()
        
        # 使用MCP管理器进行智能诊断
        diagnosis_result = await mcp_manager.diagnose_network_issue(
            request.issue_description
        )
        
        # 处理用户报告的症状
        if request.user_reported_symptoms:
            diagnosis_result["user_symptoms"] = request.user_reported_symptoms
            # 可以根据症状调整诊断结果
        
        # 考虑网络环境信息
        if request.network_environment:
            diagnosis_result["environment"] = request.network_environment
        
        return {
            "success": diagnosis_result.get("success", False),
            "data": diagnosis_result
        }
        
    except Exception as e:
        logger.error(f"网络问题诊断失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def ai_chat_diagnosis(request: ChatRequest):
    """AI聊天式网络诊断"""
    try:
        # 这里可以集成大语言模型API（如OpenRouter）
        # 结合MCP工具进行智能对话诊断
        
        user_message = request.messages[-1].content if request.messages else ""
        
        # 分析用户消息，判断是否需要调用MCP工具
        if _should_call_mcp_tools(user_message):
            # 提取问题描述并调用诊断
            issue_description = _extract_issue_from_message(user_message)
            
            if not mcp_manager.client:
                await mcp_manager.initialize()
            
            diagnosis_result = await mcp_manager.diagnose_network_issue(issue_description)
            
            # 生成AI回复
            ai_response = _generate_ai_response(diagnosis_result, user_message)
        else:
            # 普通对话回复
            ai_response = _generate_conversational_response(user_message, request.context)
        
        return {
            "success": True,
            "response": ai_response,
            "suggestions": _get_chat_suggestions(user_message)
        }
        
    except Exception as e:
        logger.error(f"AI聊天诊断失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def get_optimization_suggestions(request: AnalysisRequest):
    """获取网络优化建议"""
    try:
        # 使用MCP工具获取优化建议
        optimization_data = await _get_mcp_optimization_data()
        
        suggestions = {
            "channel_recommendations": {},
            "power_settings": {},
            "qos_settings": {},
            "general_recommendations": []
        }
        
        # 集成MCP数据
        if optimization_data.get("wifi_analysis"):
            wifi_data = optimization_data["wifi_analysis"]
            if "recommendations" in wifi_data:
                suggestions["channel_recommendations"] = wifi_data["recommendations"]
        
        # 基础优化建议
        if not suggestions["channel_recommendations"]:
            suggestions["channel_recommendations"] = {
                "2.4g": 1,
                "5g": 36,
                "reason": "避开拥挤信道"
            }
        
        suggestions["power_settings"] = {
            "tx_power": "75%",
            "reason": "平衡覆盖和干扰"
        }
        
        suggestions["qos_settings"] = {
            "enable": True,
            "priority": "video_streaming"
        }
        
        return {
            "success": True,
            "data": suggestions
        }
    except Exception as e:
        logger.error(f"获取优化建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
async def get_available_tools():
    """获取可用的诊断工具"""
    try:
        if not mcp_manager.client:
            await mcp_manager.initialize()
        
        tools = await mcp_manager.get_available_tools()
        
        return {
            "success": True,
            "tools": tools,
            "total_servers": len(tools)
        }
        
    except Exception as e:
        logger.error(f"获取诊断工具失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_mcp_status():
    """获取MCP服务状态"""
    try:
        if not mcp_manager.client:
            return {
                "success": False,
                "message": "MCP管理器未初始化",
                "servers": {}
            }
        
        server_status = await mcp_manager.get_server_status()
        
        return {
            "success": True,
            "servers": server_status,
            "initialized": True
        }
        
    except Exception as e:
        logger.error(f"获取MCP状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize")
async def initialize_mcp(background_tasks: BackgroundTasks):
    """初始化MCP管理器"""
    try:
        # 在后台任务中初始化，避免阻塞
        background_tasks.add_task(_initialize_mcp_background)
        
        return {
            "success": True,
            "message": "MCP初始化任务已启动"
        }
        
    except Exception as e:
        logger.error(f"启动MCP初始化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 辅助函数

async def _enhance_analysis_with_mcp(test_results: Dict) -> Dict:
    """使用MCP工具增强分析"""
    try:
        if not mcp_manager.client:
            return {"success": False, "error": "MCP未初始化"}
        
        # 根据测试结果类型选择合适的MCP工具
        enhancement_data = {}
        
        # 如果有WiFi相关数据
        if "wifi" in test_results or "signal" in test_results:
            wifi_result = await mcp_manager.call_tool(
                "wifi", "get_current_wifi_info", {}
            )
            if wifi_result.success:
                enhancement_data["wifi_info"] = wifi_result.data
        
        # 如果有网络连通性数据
        if "connectivity" in test_results or "ping" in test_results:
            conn_result = await mcp_manager.call_tool(
                "connectivity", "check_internet_connectivity", {}
            )
            if conn_result.success:
                enhancement_data["connectivity_info"] = conn_result.data
        
        return {
            "success": True,
            "data": enhancement_data
        }
        
    except Exception as e:
        logger.error(f"MCP增强分析失败: {str(e)}")
        return {"success": False, "error": str(e)}

async def _get_mcp_optimization_data() -> Dict:
    """获取MCP优化数据"""
    try:
        if not mcp_manager.client:
            return {}
        
        # 获取WiFi信道利用率
        channel_result = await mcp_manager.call_tool(
            "wifi", "get_wifi_channel_utilization", {}
        )
        
        optimization_data = {}
        if channel_result.success:
            optimization_data["wifi_analysis"] = channel_result.data
        
        return optimization_data
        
    except Exception as e:
        logger.error(f"获取MCP优化数据失败: {str(e)}")
        return {}

def _basic_analysis(test_results: Dict) -> Dict:
    """基础分析逻辑（当MCP不可用时）"""
    return {
        "issues": [
            "无法使用高级诊断工具，建议检查基础网络连接",
            "可能存在未检测到的网络问题"
        ],
        "recommendations": [
            "重启路由器和网络设备",
            "检查网线连接",
            "更新网络驱动程序"
        ],
        "confidence": 50,
        "priority": "medium"
    }

def _calculate_confidence(mcp_data: Dict) -> int:
    """计算诊断置信度"""
    severity = mcp_data.get("severity", "unknown")
    issues_count = len(mcp_data.get("issues_found", []))
    
    if severity == "critical":
        return min(95, 70 + issues_count * 5)
    elif severity == "high":
        return min(90, 60 + issues_count * 5)
    elif severity == "medium":
        return min(80, 50 + issues_count * 5)
    elif severity == "normal":
        return 95
    else:
        return 60

def _determine_priority(severity: str) -> str:
    """确定优先级"""
    priority_map = {
        "critical": "critical",
        "high": "high", 
        "medium": "medium",
        "normal": "low"
    }
    return priority_map.get(severity, "medium")

def _should_call_mcp_tools(message: str) -> bool:
    """判断是否需要调用MCP工具"""
    keywords = [
        "网络", "WiFi", "无线", "连接", "断网", "慢", "卡", 
        "ping", "延迟", "丢包", "DNS", "路由器", "信号"
    ]
    return any(keyword in message for keyword in keywords)

def _extract_issue_from_message(message: str) -> str:
    """从用户消息中提取问题描述"""
    # 简化实现，实际可以使用NLP技术
    return message

def _generate_ai_response(diagnosis_result: Dict, user_message: str) -> str:
    """生成AI回复"""
    if not diagnosis_result.get("success"):
        return "很抱歉，网络诊断过程中遇到了问题。建议您检查网络设备的基本连接状态。"
    
    analysis = diagnosis_result.get("analysis", {})
    issues = analysis.get("issues_found", [])
    recommendations = analysis.get("recommendations", [])
    severity = analysis.get("severity", "unknown")
    
    response = f"根据诊断结果，{analysis.get('summary', '网络状况分析完成')}。\n\n"
    
    if issues:
        response += "发现的问题：\n"
        for i, issue in enumerate(issues, 1):
            response += f"{i}. {issue}\n"
        response += "\n"
    
    if recommendations:
        response += "建议的解决方案：\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. {rec}\n"
    
    if severity == "critical":
        response += "\n⚠️ 这是严重的网络问题，建议立即处理。"
    elif severity == "high":
        response += "\n⚡ 建议尽快处理这些网络问题。"
    
    return response

def _generate_conversational_response(message: str, context: Optional[Dict]) -> str:
    """生成对话式回复"""
    # 简化实现，实际可以调用LLM API
    if "你好" in message or "帮助" in message:
        return "您好！我是网络诊断助手，可以帮您分析和解决网络问题。请描述您遇到的网络问题，我会为您进行详细诊断。"
    elif "谢谢" in message:
        return "不客气！如果您还有其他网络问题，随时可以咨询我。"
    else:
        return "我理解您的问题。如果您遇到网络故障，请详细描述具体症状，我会为您进行专业诊断。"

def _get_chat_suggestions(message: str) -> List[str]:
    """获取聊天建议"""
    suggestions = [
        "我的网络很慢，请帮我诊断",
        "WiFi连接经常断开",
        "无法访问某些网站",
        "网络延迟很高",
        "检查我的网络状态"
    ]
    return suggestions

async def _initialize_mcp_background():
    """后台初始化MCP"""
    try:
        await mcp_manager.initialize()
        logger.info("MCP管理器后台初始化完成")
    except Exception as e:
        logger.error(f"MCP后台初始化失败: {str(e)}") 