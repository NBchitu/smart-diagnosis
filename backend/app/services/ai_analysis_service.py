"""
AI网络分析服务
负责根据抓包数据生成AI分析报告
"""

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app.config.ai_config import get_ai_config
import openai
import anthropic
import requests

logger = logging.getLogger(__name__)

# 创建调试数据目录
DEBUG_DIR = Path('/tmp/ai_analysis_debug')
DEBUG_DIR.mkdir(exist_ok=True)

class AIAnalysisService:
    """AI分析服务"""
    
    def __init__(self):
        self.ai_config = get_ai_config()

    def _save_debug_data(self, task_id: str, issue_type: str, capture_summary: Dict,
                        user_description: str, prompt: str, ai_response: str = None) -> str:
        """保存调试数据到文件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_filename = f"ai_analysis_{timestamp}_{task_id[:8]}.json"
            debug_file_path = DEBUG_DIR / debug_filename

            debug_data = {
                'metadata': {
                    'task_id': task_id,
                    'timestamp': datetime.now().isoformat(),
                    'issue_type': issue_type,
                    'user_description': user_description,
                    'ai_provider': self.ai_config.current_provider,
                    'ai_model': self.ai_config.get_current_config().model if self.ai_config.get_current_config() else 'unknown'
                },
                'input_data': {
                    'capture_summary': capture_summary,
                    'prompt_length': len(prompt),
                    'prompt_content': prompt
                },
                'output_data': {
                    'ai_response': ai_response,
                    'ai_response_length': len(ai_response) if ai_response else 0
                }
            }

            with open(debug_file_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)

            logger.info(f"调试数据已保存到: {debug_file_path}")
            return str(debug_file_path)

        except Exception as e:
            logger.error(f"保存调试数据失败: {str(e)}")
            return ""

    def _update_debug_data_with_response(self, debug_file_path: str, ai_response: str):
        """更新调试数据文件，添加AI响应"""
        try:
            if os.path.exists(debug_file_path):
                with open(debug_file_path, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)

                debug_data['output_data']['ai_response'] = ai_response
                debug_data['output_data']['ai_response_length'] = len(ai_response)
                debug_data['metadata']['response_received_at'] = datetime.now().isoformat()

                with open(debug_file_path, 'w', encoding='utf-8') as f:
                    json.dump(debug_data, f, indent=2, ensure_ascii=False)

                logger.info(f"调试数据已更新: {debug_file_path}")

        except Exception as e:
            logger.error(f"更新调试数据失败: {str(e)}")
    
    def analyze_network_issue_sync(self, issue_type: str, capture_summary: Dict,
                                 user_description: Optional[str] = None, task_id: str = None) -> Dict[str, Any]:
        """
        同步版本的网络问题分析，避免事件循环冲突
        """
        ai_response = None
        debug_file_path = ""

        try:
            logger.info(f"开始同步AI分析，问题类型: {issue_type}")

            # 检查AI配置
            config = self.ai_config.get_current_config()
            if not config:
                raise Exception("AI配置无效或未设置")

            logger.info(f"使用AI提供商: {self.ai_config.current_provider}")

            # 生成分析prompt
            prompt = self._generate_analysis_prompt(issue_type, capture_summary, user_description)
            logger.info(f"生成prompt长度: {len(prompt)} 字符")

            # 保存调试数据（输入部分）
            if task_id:
                debug_file_path = self._save_debug_data(
                    task_id, issue_type, capture_summary,
                    user_description or "", prompt
                )

            # 调用AI API（同步版本）
            logger.info("开始调用AI API")
            ai_response = self._call_ai_api_sync(prompt)
            logger.info(f"AI API响应长度: {len(ai_response)} 字符")

            # 更新调试数据（输出部分）
            if task_id and debug_file_path:
                self._update_debug_data_with_response(debug_file_path, ai_response)

            # 解析AI响应
            logger.info("开始解析AI响应")
            analysis_result = self._parse_ai_response(ai_response, issue_type)

            logger.info("AI分析成功完成")
            result = {
                'success': True,
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat(),
                'ai_provider': self.ai_config.current_provider
            }

            # 添加调试文件路径到结果中
            if debug_file_path:
                result['debug_file'] = debug_file_path

            return result

        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}", exc_info=True)

            # 即使失败也保存调试数据
            if task_id and ai_response is None:
                try:
                    prompt = self._generate_analysis_prompt(issue_type, capture_summary, user_description)
                    debug_file_path = self._save_debug_data(
                        task_id, issue_type, capture_summary,
                        user_description or "", prompt, f"ERROR: {str(e)}"
                    )
                except:
                    pass

            result = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

            if debug_file_path:
                result['debug_file'] = debug_file_path

            return result

    async def analyze_network_issue(self, issue_type: str, capture_summary: Dict,
                                  user_description: Optional[str] = None) -> Dict[str, Any]:
        """
        分析网络问题

        Args:
            issue_type: 问题类型 (website_access, interconnection, game_lag, custom)
            capture_summary: 抓包数据摘要
            user_description: 用户描述的问题

        Returns:
            AI分析结果
        """
        try:
            logger.info(f"开始AI分析，问题类型: {issue_type}")

            # 生成分析prompt
            prompt = self._generate_analysis_prompt(issue_type, capture_summary, user_description)
            logger.info(f"生成的prompt长度: {len(prompt)} 字符")

            # 使用同步方法调用AI API（避免异步问题）
            ai_response = self._call_ai_api_sync(prompt)
            logger.info(f"AI响应长度: {len(ai_response)} 字符")

            # 解析AI响应
            analysis_result = self._parse_ai_response(ai_response, issue_type)
            logger.info("AI响应解析成功")

            # 保存调试数据（如果启用）
            try:
                debug_file_path = self._save_debug_data(
                    "ai_analysis", issue_type, capture_summary,
                    user_description or "", prompt, ai_response
                )
                if debug_file_path:
                    logger.info(f"调试数据已保存到: {debug_file_path}")
            except Exception as debug_e:
                logger.warning(f"保存调试数据失败: {str(debug_e)}")

            return {
                'success': True,
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat(),
                'ai_provider': self.ai_config.current_provider
            }

        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'analysis': {
                    'diagnosis': f'AI分析过程中出现错误: {str(e)}',
                    'severity': 'unknown',
                    'root_cause': '服务异常或配置问题',
                    'recommendations': ['检查AI服务状态', '验证配置信息', '重试分析'],
                    'technical_details': f'错误详情: {str(e)}',
                    'confidence': 0
                }
            }
    
    def _generate_analysis_prompt(self, issue_type: str, capture_summary: Dict, 
                                user_description: Optional[str] = None) -> str:
        """生成AI分析prompt"""
        
        # 基础prompt模板
        base_prompt = """你是一个专业的网络诊断专家，拥有丰富的网络故障排查经验。请根据以下网络抓包数据进行深度分析，识别问题根源并提供可操作的解决方案。

分析要求：
1. 仔细分析抓包数据中的关键指标
2. 识别异常模式和性能瓶颈
3. 提供具体的问题定位和解决步骤
4. 给出优化建议和预防措施

请按照以下JSON格式回复：
{
    "diagnosis": "简洁明确的问题诊断结论",
    "severity": "严重程度(low/medium/high/critical)",
    "root_cause": "详细的根本原因分析，包括技术细节",
    "key_findings": [
        "关键发现1：具体的数据异常",
        "关键发现2：性能指标问题"
    ],
    "recommendations": [
        "立即行动：紧急解决步骤",
        "短期优化：具体的配置调整",
        "长期改进：系统性优化建议"
    ],
    "diagnostic_clues": [
        "📊 具体的性能数据分析",
        "🔍 异常流量模式发现",
        "⚠️ 潜在风险点识别"
    ],
    "technical_details": "深入的技术分析和数据解读",
    "confidence": "诊断置信度(0-100)",
    "next_steps": "建议的后续监控和验证步骤"
}

"""
        
        # 重新设计的问题类型特定指导 - 专注于三大核心功能
        issue_specific_prompts = {
            'website_access': """
🌐 问题类型：网站访问问题
核心诊断重点：
- HTTP/HTTPS响应时间分析：正常<500ms，慢>2s，超时>10s
- TCP连接建立时间：正常<100ms，慢>500ms
- DNS解析时间：正常<50ms，慢>200ms
- HTTP状态码分析：2xx成功率应>95%
- 网站服务器IP归属和CDN分析

具体分析指标：
1. 计算各网站的平均响应时间和成功率
2. 分析TCP三次握手耗时
3. 检查HTTP错误状态码分布
4. 评估不同网站的访问质量差异
5. 识别CDN节点选择是否合理

网站访问性能评估标准：
- 📊 优秀：HTTP响应<300ms，成功率>98%
- 📊 良好：HTTP响应300-800ms，成功率95-98%
- 📊 一般：HTTP响应800-2000ms，成功率90-95%
- 📊 较差：HTTP响应>2000ms，成功率<90%

常见问题和解决方案：
- DNS解析慢 → 更换DNS服务器(如8.8.8.8)
- CDN节点远 → 联系网站方优化CDN配置
- 运营商线路问题 → 尝试使用VPN或代理
- 本地网络拥塞 → 检查带宽使用情况
""",
            'interconnection': """
� 问题类型：互联互通访问
核心诊断重点：
- 跨运营商访问延迟：移动↔联通↔电信
- 不同ISP服务器的访问质量对比
- 互联互通节点的性能瓶颈识别
- 路由路径优化分析

具体分析指标：
1. 识别目标服务器的ISP归属
2. 计算跨运营商访问的RTT延迟
3. 分析不同运营商线路的丢包率
4. 评估互联互通质量等级
5. 检测路由绕行和次优路径

互联互通质量评估：
- 📊 优秀：跨网延迟<50ms，丢包率<0.1%
- 📊 良好：跨网延迟50-100ms，丢包率0.1-0.5%
- 📊 一般：跨网延迟100-200ms，丢包率0.5-1%
- 📊 较差：跨网延迟>200ms，丢包率>1%

运营商互联分析：
- 中国移动 ↔ 中国联通：重点关注北方地区互联质量
- 中国移动 ↔ 中国电信：重点关注南方地区互联质量
- 教育网 ↔ 商业网：关注学术资源访问质量

优化建议：
- 选择同运营商服务器 → 避免跨网访问
- 使用CDN加速 → 就近访问优质节点
- 多线路接入 → BGP多线或双线接入
- 联系运营商 → 反馈互联质量问题
""",
            'game_lag': """
� 问题类型：游戏卡顿问题
核心诊断重点：
- 游戏流量识别和服务器IP归属分析
- 游戏服务器是否为中国移动网络
- UDP包丢失率和延迟抖动分析
- 游戏专用端口的连接质量

游戏流量识别算法：
1. 端口特征：7000-8100, 17500-17600, 10000-15000
2. 协议特征：UDP占比>60%，包大小50-800字节
3. 流量模式：高频率双向通信，有规律心跳包
4. 时序特征：30-60fps对应的包发送频率

游戏服务器ISP分析：
- 🎯 中国移动游戏服务器：延迟<30ms，最优体验
- 🎯 中国联通游戏服务器：延迟30-50ms，良好体验
- 🎯 中国电信游戏服务器：延迟50-80ms，一般体验
- 🎯 海外游戏服务器：延迟>100ms，需要优化

游戏网络质量评估：
- � 优秀：延迟<30ms，丢包率<0.01%，抖动<5ms
- 📊 良好：延迟30-50ms，丢包率0.01-0.1%，抖动5-10ms
- 📊 一般：延迟50-80ms，丢包率0.1-0.5%，抖动10-20ms
- 📊 较差：延迟>80ms，丢包率>0.5%，抖动>20ms

游戏优化建议：
- 选择移动游戏服务器 → 获得最佳网络体验
- 关闭后台应用 → 减少网络带宽占用
- 使用游戏加速器 → 优化路由路径
- 升级网络套餐 → 提高带宽和优先级
- 使用有线连接 → 避免WiFi不稳定
""",
            'custom': """
🔧 问题类型：自定义网络问题
核心诊断重点：
- 全面的网络性能基线分析
- 异常流量模式识别
- 协议分布和应用行为分析
- 安全威胁和异常连接检测

具体分析指标：
1. 建立网络性能基线指标
2. 识别异常的流量模式和峰值
3. 分析应用层协议的使用情况
4. 检测潜在的安全威胁
5. 评估整体网络健康状况

通用分析方法：
- 流量分析 → 识别异常应用和用户行为
- 性能监控 → 建立关键指标的监控体系
- 安全检查 → 发现潜在的安全风险
- 容量规划 → 预测未来的网络需求
"""
        }
        
        # 构建完整prompt
        prompt = base_prompt

        # 添加问题类型特定的分析指导
        if issue_type in issue_specific_prompts:
            prompt += issue_specific_prompts[issue_type]
        else:
            prompt += issue_specific_prompts.get('custom', '')

        # 添加用户描述
        if user_description:
            prompt += f"\n📝 用户描述的问题：{user_description}\n"

        # 添加抓包环境信息
        prompt += "\n🔍 抓包环境信息：\n"
        if capture_summary.get('statistics'):
            stats = capture_summary['statistics']
            prompt += f"- 抓包时长: {stats.get('duration', 'N/A')}秒\n"
            prompt += f"- 总包数: {stats.get('total_packets', 'N/A')}\n"
            prompt += f"- 数据量: {stats.get('total_bytes', 'N/A')}字节\n"

        # 添加关键性能指标
        if capture_summary.get('enhanced_analysis'):
            enhanced = capture_summary['enhanced_analysis']
            prompt += "\n📊 关键性能指标：\n"

            if enhanced.get('network_quality'):
                nq = enhanced['network_quality']
                prompt += f"- 平均RTT: {nq.get('avg_rtt', 'N/A')}ms\n"
                prompt += f"- 丢包率: {nq.get('packet_loss_rate', 0)*100:.2f}%\n"
                prompt += f"- 重传次数: {nq.get('retransmissions', 'N/A')}\n"

            if enhanced.get('http_analysis'):
                http = enhanced['http_analysis']
                prompt += f"- HTTP请求数: {http.get('total_requests', 'N/A')}\n"
                prompt += f"- 访问域名数: {http.get('unique_domains', 'N/A')}\n"
                prompt += f"- HTTPS比例: {http.get('https_ratio', 0)*100:.1f}%\n"

        # 添加详细的抓包数据
        prompt += f"\n📋 详细抓包数据：\n{json.dumps(capture_summary, indent=2, ensure_ascii=False)}\n"

        # 添加分析要求
        prompt += """
🎯 分析要求：
1. 重点关注异常指标和性能瓶颈
2. 提供具体的数值分析和对比
3. 给出可操作的解决步骤
4. 包含预防措施和监控建议
5. 评估问题的紧急程度和影响范围

请严格按照上述JSON格式回复，确保所有字段都有实际内容："""

        return prompt

    def _call_ai_api_sync(self, prompt: str) -> str:
        """同步版本的AI API调用"""
        try:
            config = self.ai_config.get_current_config()
            logger.info(f"获取AI配置: {config is not None}")

            if not config:
                logger.error("AI配置无效或未找到")
                raise Exception("AI配置无效：请检查环境变量设置")

            logger.info(f"调用AI API，提供商: {self.ai_config.current_provider}")
            logger.info(f"API配置 - 模型: {config.model}, 基础URL: {config.base_url}")

            if self.ai_config.current_provider == 'openrouter':
                result = self._call_openrouter_api_sync(prompt, config)
            elif self.ai_config.current_provider == 'openai':
                result = self._call_openai_api_sync(prompt, config)
            elif self.ai_config.current_provider == 'anthropic':
                result = self._call_anthropic_api_sync(prompt, config)
            else:
                raise Exception(f"不支持的AI提供商: {self.ai_config.current_provider}")

            logger.info("AI API调用成功")
            return result

        except Exception as e:
            logger.error(f"AI API调用失败: {str(e)}", exc_info=True)
            raise

    async def _call_ai_api(self, prompt: str) -> str:
        """调用AI API"""
        config = self.ai_config.get_current_config()
        if not config:
            raise Exception("AI配置无效")
        
        try:
            if self.ai_config.current_provider == 'openrouter':
                return await self._call_openrouter_api(prompt, config)
            elif self.ai_config.current_provider == 'openai':
                return await self._call_openai_api(prompt, config)
            elif self.ai_config.current_provider == 'anthropic':
                return await self._call_anthropic_api(prompt, config)
            else:
                raise Exception(f"不支持的AI提供商: {self.ai_config.current_provider}")
                
        except Exception as e:
            logger.error(f"AI API调用失败: {str(e)}")
            raise
    
    async def _call_openrouter_api(self, prompt: str, config) -> str:
        """调用OpenRouter API"""
        import aiohttp

        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:3000',
            'X-Title': 'Network Packet Analysis'
        }

        data = {
            'model': config.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': config.max_tokens,
            'temperature': config.temperature
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API错误: {response.status} - {error_text}")

                result = await response.json()
                return result['choices'][0]['message']['content']

    def _call_openrouter_api_sync(self, prompt: str, config) -> str:
        """同步调用OpenRouter API"""
        import requests

        try:
            logger.info(f"准备调用OpenRouter API: {config.base_url}")
            logger.info(f"使用模型: {config.model}")
            logger.info(f"Prompt长度: {len(prompt)} 字符")
            headers = {
                'Authorization': f'Bearer {config.api_key}',  # 隐藏API密钥
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Network Packet Analysis'
            }

            data = {
                'model': config.model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': config.max_tokens,
                'temperature': config.temperature
            }

            logger.info(f"发送请求到: {config.base_url}/chat/completions")

            response = requests.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=config.timeout
            )

            logger.info(f"API响应状态码: {response.status_code}")

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"API错误响应: {error_text}")
                raise Exception(f"OpenRouter API错误: {response.status_code} - {error_text}")

            result = response.json()
            logger.info("API响应解析成功")

            if 'choices' not in result or not result['choices']:
                logger.error(f"API响应格式异常: {result}")
                raise Exception("API响应中没有choices字段")

            content = result['choices'][0]['message']['content']
            logger.info(f"获取到AI响应，长度: {len(content)} 字符")

            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {str(e)}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"OpenRouter API调用失败: {str(e)}")
            raise

    def _call_openai_api_sync(self, prompt: str, config) -> str:
        """同步调用OpenAI API"""
        import openai

        client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        return response.choices[0].message.content

    def _call_anthropic_api_sync(self, prompt: str, config) -> str:
        """同步调用Anthropic API"""
        import anthropic

        client = anthropic.Anthropic(api_key=config.api_key)

        response = client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )

        return response.content[0].text

    async def _call_openai_api(self, prompt: str, config) -> str:
        """调用OpenAI API"""
        client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic_api(self, prompt: str, config) -> str:
        """调用Anthropic API"""
        client = anthropic.Anthropic(api_key=config.api_key)
        
        response = client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        
        return response.content[0].text
    
    def _parse_ai_response(self, ai_response: str, issue_type: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            logger.info(f"开始解析AI响应，长度: {len(ai_response)} 字符")
            logger.debug(f"AI响应前100字符: {ai_response[:100]}")

            # 清理响应文本
            cleaned_response = ai_response.strip()

            # 尝试解析JSON响应
            if cleaned_response.startswith('{') and cleaned_response.endswith('}'):
                logger.info("检测到完整JSON格式响应")
                analysis = json.loads(cleaned_response)
            else:
                # 如果不是完整JSON格式，尝试提取JSON部分
                import re
                logger.info("尝试从响应中提取JSON部分")

                # 更强的JSON提取模式
                json_patterns = [
                    r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 简单嵌套JSON
                    r'\{.*?\}(?=\s*$)',  # 到结尾的JSON
                    r'\{.*\}',  # 最宽泛的匹配
                ]

                analysis = None
                for pattern in json_patterns:
                    json_match = re.search(pattern, cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            json_text = json_match.group()
                            logger.info(f"找到JSON匹配，长度: {len(json_text)} 字符")
                            analysis = json.loads(json_text)
                            logger.info("JSON解析成功")
                            break
                        except json.JSONDecodeError as je:
                            logger.warning(f"JSON解析失败: {str(je)}")
                            continue

                if analysis is None:
                    # 如果无法解析JSON，创建默认结构并包含AI的文本响应
                    logger.info("无法解析JSON，创建默认结构")
                    analysis = {
                        'diagnosis': ai_response[:200] + '...' if len(ai_response) > 200 else ai_response,
                        'severity': 'medium',
                        'root_cause': '需要进一步分析，AI返回了非结构化响应',
                        'key_findings': ['AI已提供分析，但格式需要调整'],
                        'recommendations': [
                            '请查看技术细节中的完整AI分析',
                            '建议重新进行结构化分析',
                            '如需要，请联系网络管理员'
                        ],
                        'diagnostic_clues': [
                            '📋 AI已完成分析但返回格式不标准',
                            '🔍 请查看技术细节获取完整信息',
                            '⚠️ 建议使用结构化分析模式'
                        ],
                        'technical_details': ai_response,
                        'confidence': 60,
                        'next_steps': '建议重新进行分析以获得结构化结果'
                    }
            
            # 验证和补充必要字段
            required_fields = {
                'diagnosis': '网络问题分析中',
                'severity': 'medium',
                'root_cause': '正在分析根本原因',
                'recommendations': ['请稍后查看详细分析结果'],
                'technical_details': '技术分析进行中',
                'confidence': 70
            }

            for field, default_value in required_fields.items():
                if field not in analysis:
                    analysis[field] = default_value

            # 确保列表字段是列表格式
            list_fields = ['recommendations', 'key_findings', 'diagnostic_clues']
            for field in list_fields:
                if field in analysis and not isinstance(analysis[field], list):
                    analysis[field] = [str(analysis[field])] if analysis[field] else []
                elif field not in analysis:
                    analysis[field] = []

            # 确保数值字段是数字
            if 'confidence' in analysis:
                try:
                    analysis['confidence'] = int(analysis['confidence'])
                except (ValueError, TypeError):
                    analysis['confidence'] = 70

            return analysis
            
        except Exception as e:
            logger.error(f"解析AI响应失败: {str(e)}", exc_info=True)
            logger.error(f"AI响应内容: {ai_response[:500]}...")

            # 尝试保存调试信息
            try:
                debug_info = {
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'ai_response_length': len(ai_response),
                    'ai_response_preview': ai_response[:200],
                    'issue_type': issue_type,
                    'timestamp': datetime.now().isoformat()
                }
                logger.error(f"调试信息: {debug_info}")
            except:
                pass

            return {
                'diagnosis': '分析结果解析失败，但已获取到AI响应',
                'severity': 'medium',
                'root_cause': f'响应解析错误: {str(e)}，原始响应长度: {len(ai_response)}字符',
                'key_findings': ['AI分析已完成，但响应格式需要调整'],
                'recommendations': [
                    '请检查AI服务配置',
                    '尝试重新进行分析',
                    '如问题持续，请联系技术支持'
                ],
                'diagnostic_clues': [
                    f'📋 AI响应长度: {len(ai_response)}字符',
                    f'🔍 解析错误: {str(e)}',
                    f'🔧 错误类型: {type(e).__name__}',
                    '⚠️ 建议检查AI服务状态'
                ],
                'technical_details': f'解析错误详情: {str(e)}\n错误类型: {type(e).__name__}\n\n原始AI响应:\n{ai_response[:1000]}...' if len(ai_response) > 1000 else f'解析错误详情: {str(e)}\n错误类型: {type(e).__name__}\n\n原始AI响应:\n{ai_response}',
                'confidence': 30,
                'next_steps': '建议重新进行分析或联系技术支持'
            }

# 全局AI分析服务实例
ai_analysis_service = AIAnalysisService()

def get_ai_analysis_service() -> AIAnalysisService:
    """获取AI分析服务实例"""
    return ai_analysis_service
