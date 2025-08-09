import { NextRequest } from 'next/server';
import { generateText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

// 扩展全局对象类型
declare global {
  var diagnosticPlan: any;
}

// 步进式诊断请求接口
interface StepwiseDiagnosisRequest {
  message: string;
  action: 'analyze' | 'get_next_step' | 'evaluate_result';
  context?: {
    currentStep: number;
    totalSteps: number;
    executedTools: Array<{
      id: string;
      name: string;
      result: any;
      timestamp: string;
    }>;
    originalProblem: string;
  };
  toolResult?: any;
}

// 步进式诊断响应接口
interface StepwiseDiagnosisResponse {
  success: boolean;
  data?: {
    type: 'analysis' | 'next_step' | 'evaluation' | 'completion';
    analysis?: string;
    reasoning?: string;
    urgency?: 'high' | 'medium' | 'low';
    totalSteps?: number;
    currentStep?: number;
    nextTool?: ToolRecommendation;
    evaluation?: {
      summary: string;
      findings: string[];
      recommendations: string[];
      needsNextStep: boolean;
    };
    isComplete?: boolean;
    finalSummary?: string;
  };
  error?: string;
}

// 工具推荐接口
interface ToolRecommendation {
  id: string;
  name: string;
  description: string;
  category: 'network' | 'wifi' | 'connectivity' | 'gateway' | 'packet';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  estimatedDuration: string;
  parameters: Array<{
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    defaultValue?: any;
    options?: string[];
    required: boolean;
    description: string;
  }>;
  apiEndpoint: string;
  reasoning: string;
}

// 创建AI客户端
function createAIClient() {
  try {
    const provider = process.env.AI_PROVIDER || 'openrouter';
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    if (provider === 'openrouter' && openRouterKey && openRouterKey.length > 10) {
      const openai = createOpenAI({
        baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
        apiKey: openRouterKey,
      });
      return openai(process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku');
    }
    
    if (provider === 'openai' && openAIKey && openAIKey.startsWith('sk-')) {
      const openai = createOpenAI({
        apiKey: openAIKey,
      });
      return openai(process.env.OPENAI_MODEL || 'gpt-4o-mini');
    }

    return null;
  } catch (error) {
    console.error('❌ 创建AI客户端失败:', error);
    return null;
  }
}

// 预定义的工具模板
const TOOL_TEMPLATES: Record<string, Omit<ToolRecommendation, 'reasoning'>> = {
  ping: {
    id: 'ping',
    name: 'Ping测试',
    description: '测试与指定主机的网络连通性和延迟',
    category: 'network',
    priority: 'high',
    icon: '🏓',
    estimatedDuration: '5-10秒',
    parameters: [
      {
        name: 'host',
        type: 'string',
        label: '目标主机',
        defaultValue: 'baidu.com',
        required: true,
        description: '要测试的主机地址或域名'
      },
      {
        name: 'count',
        type: 'number',
        label: '测试次数',
        defaultValue: 4,
        required: false,
        description: 'ping测试的次数'
      }
    ],
    apiEndpoint: '/api/network-ping'
  },
  speed_test: {
    id: 'speed_test',
    name: '网络测速',
    description: '测试网络上传下载速度和延迟',
    category: 'network',
    priority: 'high',
    icon: '⚡',
    estimatedDuration: '30-60秒',
    parameters: [],
    apiEndpoint: '/api/speed-test'
  },
  traceroute: {
    id: 'traceroute',
    name: '路由追踪',
    description: '追踪数据包到目标主机的传输路径',
    category: 'network',
    priority: 'high',
    icon: '🛤️',
    estimatedDuration: '15-30秒',
    parameters: [
      {
        name: 'host',
        type: 'string',
        label: '目标主机',
        defaultValue: 'baidu.com',
        required: true,
        description: '要追踪路由的主机地址或域名'
      }
    ],
    apiEndpoint: '/api/traceroute'
  },
  dns_test: {
    id: 'dns_test',
    name: 'DNS测试',
    description: '测试域名解析速度和准确性',
    category: 'connectivity',
    priority: 'high',
    icon: '🌐',
    estimatedDuration: '10-20秒',
    parameters: [
      {
        name: 'domain',
        type: 'string',
        label: '域名',
        defaultValue: 'baidu.com',
        required: true,
        description: '要测试解析的域名'
      }
    ],
    apiEndpoint: '/api/dns-test'
  },
  wifi_scan: {
    id: 'wifi_scan',
    name: 'WiFi扫描',
    description: '扫描周围的WiFi网络并分析信号强度',
    category: 'wifi',
    priority: 'medium',
    icon: '📶',
    estimatedDuration: '10-15秒',
    parameters: [],
    apiEndpoint: '/api/wifi-scan'
  },
  connectivity_check: {
    id: 'connectivity_check',
    name: '连通性检查',
    description: '全面检查互联网连接状态',
    category: 'connectivity',
    priority: 'high',
    icon: '🌐',
    estimatedDuration: '15-20秒',
    parameters: [
      {
        name: 'testHosts',
        type: 'select',
        label: '测试目标',
        defaultValue: 'default',
        options: ['default', 'international', 'china'],
        required: false,
        description: '选择测试的目标服务器组'
      }
    ],
    apiEndpoint: '/api/connectivity-check'
  },
  gateway_info: {
    id: 'gateway_info',
    name: '网关信息',
    description: '获取网络网关和路由信息',
    category: 'gateway',
    priority: 'medium',
    icon: '🖥️',
    estimatedDuration: '3-5秒',
    parameters: [],
    apiEndpoint: '/api/gateway-info'
  },
  packet_capture: {
    id: 'packet_capture',
    name: '数据包分析',
    description: '捕获和分析网络数据包',
    category: 'packet',
    priority: 'low',
    icon: '🔍',
    estimatedDuration: '30-60秒',
    parameters: [
      {
        name: 'target',
        type: 'string',
        label: '分析目标',
        defaultValue: 'sina.com',
        required: true,
        description: '要分析的网站或IP地址'
      },
      {
        name: 'duration',
        type: 'number',
        label: '捕获时长(秒)',
        defaultValue: 30,
        required: false,
        description: '数据包捕获的持续时间'
      }
    ],
    apiEndpoint: '/api/packet-capture'
  },
  port_scan: {
    id: 'port_scan',
    name: '端口扫描',
    description: '检测目标主机的开放端口',
    category: 'packet',
    priority: 'medium',
    icon: '🔍',
    estimatedDuration: '20-40秒',
    parameters: [
      {
        name: 'host',
        type: 'string',
        label: '目标主机',
        defaultValue: 'baidu.com',
        required: true,
        description: '要扫描的主机地址或域名'
      },
      {
        name: 'ports',
        type: 'string',
        label: '端口范围',
        defaultValue: '80,443,22,21,25,53',
        required: false,
        description: '要扫描的端口，用逗号分隔'
      }
    ],
    apiEndpoint: '/api/port-scan'
  },
  ssl_check: {
    id: 'ssl_check',
    name: 'SSL证书检查',
    description: '检查网站SSL证书状态和安全性',
    category: 'connectivity',
    priority: 'medium',
    icon: '🔒',
    estimatedDuration: '5-10秒',
    parameters: [
      {
        name: 'host',
        type: 'string',
        label: '网站地址',
        defaultValue: 'baidu.com',
        required: true,
        description: '要检查SSL证书的网站域名'
      }
    ],
    apiEndpoint: '/api/ssl-check'
  },
  network_quality: {
    id: 'network_quality',
    name: '网络质量监控',
    description: '持续监控网络质量指标',
    category: 'network',
    priority: 'low',
    icon: '📊',
    estimatedDuration: '60-120秒',
    parameters: [
      {
        name: 'duration',
        type: 'number',
        label: '监控时长(秒)',
        defaultValue: 60,
        required: false,
        description: '网络质量监控的持续时间'
      }
    ],
    apiEndpoint: '/api/network-quality'
  }
};

// 分析用户问题并生成诊断计划
async function analyzeUserProblem(message: string, aiModel: any): Promise<any> {
  const analysisPrompt = `
作为网络诊断专家，请分析用户的网络问题并制定逐步诊断计划。

用户问题：${message}

可用的诊断工具：
基础诊断工具：
1. ping - 测试网络连通性、延迟及稳定性。
2. speed_test - 测试网络上传下载速度。
3. wifi_scan - 扫描WiFi网络，发现WiFi信号弱覆盖或者干扰引起的网络不稳定。
4. connectivity_check - 全面的网络连通性检查，用于对比各家运营商的网络连通性差异，通常用来验证用户所反馈的在中国移动网络下无法访问网站或app，但在电信下却可以访问的问题。

高级诊断工具：
5. traceroute - 追踪数据包传输路径，用于深入发现哪个环节产生了丢包
6. dns_test - 测试域名解析速度，用户发现是否因为DNS配置错误导致的CDN分配问题，比如中国移动用户配置了电信DNS，导致分配到电信CDN，引起视频、游戏跨运营商访问产生的网速慢/加载缓慢问题
7. gateway_info - 获取网关信息
8. packet_capture - 数据包分析，通过网络抓包来发现深层次的网络问题，比如互联互通问题

专业诊断工具（很少用到）：
9. port_scan - 检测主机开放端口
10. ssl_check - 检查SSL证书状态
11. network_quality - 持续监控网络质量

请以JSON格式回复，包含：
{
  "analysis": "问题分析",
  "reasoning": "诊断思路",
  "urgency": "high|medium|low",
  "totalSteps": 步骤数量,
  "diagnosticPlan": ["tool1", "tool2", "tool3"],
  "stepReasons": ["步骤1原因", "步骤2原因", "步骤3原因"]
}

要求：
1. 要仔细分析用户问题描述,给出的诊断步骤要符合逻辑
2. 工具顺序要合理（从基础到高级）
3. 每步都要有明确的诊断目的
4. 通常2-4个步骤比较合适
`;

  const { text } = await generateText({
    model: aiModel,
    prompt: analysisPrompt,
    temperature: 0.3,
  });

  try {
    console.log(`==============AI网络诊断结果-Start==============`);
    console.log(text);
    console.log(`==============AI网络诊断结果-End==============`);
    return JSON.parse(text);
    
  } catch (error) {
    console.error('❌ AI分析结果解析失败:', error);
    return {
      analysis: "AI分析结果解析失败，将采用默认诊断流程",
      reasoning: "系统将按照标准流程进行诊断",
      urgency: "medium",
      totalSteps: 2,
      diagnosticPlan: ["ping", "connectivity_check"],
      stepReasons: ["首先测试基础连通性", "然后进行全面连通性检查"]
    };
  }
}

// 获取下一步工具
function getNextStepTool(plan: any, currentStep: number): ToolRecommendation | null {
  if (currentStep >= plan.totalSteps || currentStep >= plan.diagnosticPlan.length) {
    return null;
  }

  const toolId = plan.diagnosticPlan[currentStep];
  const toolTemplate = TOOL_TEMPLATES[toolId];
  
  if (!toolTemplate) {
    return null;
  }

  return {
    ...toolTemplate,
    reasoning: plan.stepReasons[currentStep] || `执行${toolTemplate.name}以进行诊断`
  };
}

// 评估工具执行结果
async function evaluateToolResult(toolId: string, result: any, context: any, aiModel: any): Promise<any> {
  // 简化评估逻辑，优先使用预设模板
  const quickEvaluation = getQuickEvaluation(toolId, result, context);
  if (quickEvaluation) {
    console.log('🚀 使用快速评估模板');
    return quickEvaluation;
  }

  // 如果需要AI评估，设置超时机制
  console.log('🤖 使用AI评估，设置超时保护...');
  const evaluationPrompt = `
网络诊断工具评估：

问题：${context.originalProblem}
工具：${toolId}
结果：${JSON.stringify(result, null, 2)}

请简洁回复JSON：
{
  "summary": "简短总结",
  "findings": ["主要发现"],
  "recommendations": ["关键建议"],
  "needsNextStep": ${context.currentStep < context.totalSteps - 1},
  "nextStepReason": "继续原因"
}
`;

  try {
    // 设置10秒超时
    const evaluationPromise = generateText({
      model: aiModel,
      prompt: evaluationPrompt,
      temperature: 0.3,
    });

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('AI评估超时')), 10000);
    });

    const { text } = await Promise.race([evaluationPromise, timeoutPromise]) as any;
    return JSON.parse(text);
    
  } catch (error) {
    console.error('❌ AI评估失败，使用备用方案:', error);
    return getFallbackEvaluation(toolId, result, context);
  }
}

// 快速评估模板（无需AI）
function getQuickEvaluation(toolId: string, result: any, context: any): any | null {
  console.log('🔍 快速评估 - 工具ID:', toolId, '结果:', result);

  switch (toolId) {
    case 'ping':
    case 'ping_test':
      return evaluatePingResult(result, context);

    case 'wifi_scan':
      return evaluateWiFiScanResult(result, context);

    case 'connectivity_check':
      return evaluateConnectivityResult(result, context);

    case 'website_accessibility_test':
      return evaluateWebsiteAccessibilityResult(result, context);

    case 'gateway_info':
    case 'gateway_info_check':
      return evaluateGatewayInfoResult(result, context);

    default:
      return null; // 其他工具需要AI评估
  }
}

// Ping测试结果评估
function evaluatePingResult(result: any, context: any): any {
  console.log('🏓 评估Ping结果:', result);

  // 处理不同的数据结构
  let data = result;
  if (result.data) {
    data = result.data;
  }

  const host = data.host || data.target || 'unknown';
  const packetsSent = parseInt(data.packets_sent || data.packets_transmitted || '0');
  const packetsReceived = parseInt(data.packets_received || '0');
  const packetLossStr = data.packet_loss || '0%';
  const packetLoss = parseFloat(packetLossStr.replace('%', ''));
  const avgLatencyStr = data.avg_latency || data.avg_time || '0ms';
  const avgLatency = parseFloat(avgLatencyStr.replace('ms', ''));

  let summary = `Ping测试完成 - ${host}`;
  let findings = [];
  let recommendations = [];

  // 分析连通性
  if (packetLoss === 0 && packetsReceived > 0) {
    summary = `网络连通性正常 - ${host}`;
    findings.push(`✅ 目标主机可达，发送${packetsSent}个数据包，全部收到回复`);
  } else if (packetLoss > 0 && packetLoss < 100) {
    summary = `网络连通性不稳定 - ${host}`;
    findings.push(`⚠️ 检测到${packetLoss}%丢包 (${packetsReceived}/${packetsSent})`);
    recommendations.push("检查网络连接稳定性");
    recommendations.push("可能存在网络拥塞或设备故障");
  } else if (packetLoss === 100 || packetsReceived === 0) {
    summary = `网络连通性失败 - ${host}`;
    findings.push(`❌ 目标主机不可达，所有数据包丢失`);
    recommendations.push("检查目标地址是否正确");
    recommendations.push("检查网络连接和防火墙设置");
  }

  // 分析延迟
  if (avgLatency > 0) {
    if (avgLatency < 30) {
      findings.push(`🚀 延迟优秀 (${avgLatency}ms) - 网络响应非常快`);
    } else if (avgLatency < 100) {
      findings.push(`✅ 延迟良好 (${avgLatency}ms) - 网络响应正常`);
    } else if (avgLatency < 300) {
      findings.push(`⚠️ 延迟偏高 (${avgLatency}ms) - 可能影响实时应用`);
      recommendations.push("检查网络质量和带宽使用情况");
    } else {
      findings.push(`❌ 延迟过高 (${avgLatency}ms) - 网络响应缓慢`);
      recommendations.push("检查网络质量、路由和ISP连接");
      recommendations.push("考虑更换网络服务提供商或优化网络配置");
    }
  }

  return {
    summary,
    findings,
    recommendations,
    needsNextStep: context.currentStep < context.totalSteps - 1,
    nextStepReason: "继续检查其他网络指标以获得完整诊断"
  };
}

// WiFi扫描结果评估
function evaluateWiFiScanResult(result: any, context: any): any {
  console.log('📶 评估WiFi扫描结果:', result);

  const data = result.data || result;
  const currentWifi = data.current_wifi || {};
  const nearbyNetworks = data.nearby_networks || [];
  const channelAnalysis = data.channel_analysis || {};

  let summary = "WiFi扫描完成";
  let findings = [];
  let recommendations = [];

  // 分析当前WiFi连接
  if (currentWifi.ssid) {
    const signalStrength = currentWifi.signal_strength || -70;
    const signalQuality = currentWifi.signal_quality || 0;

    summary = `WiFi扫描完成 - 当前连接: ${currentWifi.ssid}`;

    if (signalStrength > -50) {
      findings.push(`📶 WiFi信号强度优秀 (${signalStrength}dBm, ${signalQuality}%)`);
    } else if (signalStrength > -70) {
      findings.push(`📶 WiFi信号强度良好 (${signalStrength}dBm, ${signalQuality}%)`);
    } else {
      findings.push(`📶 WiFi信号强度较弱 (${signalStrength}dBm, ${signalQuality}%)`);
      recommendations.push("尝试靠近路由器或调整设备位置");
    }
  }

  // 分析周边网络
  if (nearbyNetworks.length > 0) {
    findings.push(`🔍 发现${nearbyNetworks.length}个周边WiFi网络`);

    const strongNetworks = nearbyNetworks.filter((n: any) => (n.signal || n.signal_strength || -100) > -60);
    if (strongNetworks.length > 5) {
      findings.push(`⚠️ 周边有${strongNetworks.length}个强信号网络，可能存在干扰`);
      recommendations.push("考虑更换WiFi信道以减少干扰");
    }
  }

  // 分析信道干扰
  if (channelAnalysis.interference_level) {
    const level = channelAnalysis.interference_level;
    if (level === 'high') {
      findings.push(`🚨 当前信道干扰严重`);
      recommendations.push("强烈建议更换WiFi信道");
    } else if (level === 'medium') {
      findings.push(`⚠️ 当前信道存在中等干扰`);
      recommendations.push("建议考虑更换WiFi信道");
    } else {
      findings.push(`✅ 当前信道干扰较少`);
    }
  }

  return {
    summary,
    findings,
    recommendations,
    needsNextStep: context.currentStep < context.totalSteps - 1,
    nextStepReason: "继续检查网络连通性和其他指标"
  };
}

// 连通性检查结果评估
function evaluateConnectivityResult(result: any, context: any): any {
  console.log('🌐 评估连通性检查结果:', result);

  const data = result.data || result;
  const tests = data.tests || [];

  let summary = "网络连通性检查完成";
  let findings = [];
  let recommendations = [];

  if (tests.length > 0) {
    const successfulTests = tests.filter((t: any) => t.success || t.status === 'success');
    const failedTests = tests.filter((t: any) => !t.success && t.status !== 'success');

    if (failedTests.length === 0) {
      summary = "网络连通性正常";
      findings.push(`✅ 所有${tests.length}项连通性测试均通过`);
      findings.push("互联网连接正常，DNS解析正常");
    } else if (successfulTests.length > failedTests.length) {
      summary = "网络连通性部分异常";
      findings.push(`⚠️ ${successfulTests.length}/${tests.length}项测试通过`);
      findings.push(`${failedTests.length}项测试失败: ${failedTests.map((t: any) => t.target || t.host).join(', ')}`);
      recommendations.push("检查失败的连接目标");
      recommendations.push("可能存在DNS或防火墙问题");
    } else {
      summary = "网络连通性严重异常";
      findings.push(`❌ 大部分连通性测试失败 (${failedTests.length}/${tests.length})`);
      recommendations.push("检查网络连接和路由器设置");
      recommendations.push("联系网络服务提供商");
    }
  }

  return {
    summary,
    findings,
    recommendations,
    needsNextStep: context.currentStep < context.totalSteps - 1,
    nextStepReason: "继续深入分析网络问题"
  };
}

// 网站可访问性测试结果评估
function evaluateWebsiteAccessibilityResult(result: any, context: any): any {
  console.log('🌍 评估网站可访问性结果:', result);

  const data = result.data || result;
  const url = data.url || data.target || 'unknown';
  const testResults = data.results || [];

  let summary = `网站可访问性测试完成 - ${url}`;
  let findings = [];
  let recommendations = [];

  if (testResults.length > 0) {
    // 分析多运营商测试结果
    const accessibleResults = testResults.filter((r: any) => r.accessible === true);
    const failedResults = testResults.filter((r: any) => r.accessible === false);

    if (accessibleResults.length === testResults.length) {
      // 所有运营商都能访问
      summary = `网站访问正常 - ${url}`;
      findings.push(`✅ 所有${testResults.length}个运营商网络均可正常访问`);

      // 分析响应时间
      const responseTimes = accessibleResults
        .filter((r: any) => r.response_time > 0)
        .map((r: any) => r.response_time);

      if (responseTimes.length > 0) {
        const avgResponseTime = Math.round(responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length);
        const minResponseTime = Math.min(...responseTimes);
        const maxResponseTime = Math.max(...responseTimes);

        if (avgResponseTime < 1000) {
          findings.push(`🚀 平均响应速度优秀 (${avgResponseTime}ms, 范围: ${minResponseTime}-${maxResponseTime}ms)`);
        } else if (avgResponseTime < 3000) {
          findings.push(`✅ 平均响应速度良好 (${avgResponseTime}ms, 范围: ${minResponseTime}-${maxResponseTime}ms)`);
        } else {
          findings.push(`⚠️ 平均响应速度较慢 (${avgResponseTime}ms, 范围: ${minResponseTime}-${maxResponseTime}ms)`);
          recommendations.push("网站响应较慢，可能影响用户体验");
        }
      }

      // 检查是否有运营商差异
      if (responseTimes.length > 1) {
        const maxDiff = Math.max(...responseTimes) - Math.min(...responseTimes);
        if (maxDiff > 1000) {
          findings.push(`⚠️ 不同运营商响应时间差异较大 (${maxDiff}ms)`);
          recommendations.push("某些运营商访问较慢，可能存在网络路由问题");
        }
      }

    } else if (accessibleResults.length > 0) {
      // 部分运营商可以访问
      summary = `网站访问部分异常 - ${url}`;
      findings.push(`⚠️ ${accessibleResults.length}/${testResults.length}个运营商网络可以访问`);

      // 列出可访问的运营商
      const accessibleCarriers = accessibleResults.map((r: any) => r.carrier).join('、');
      findings.push(`✅ 可访问运营商: ${accessibleCarriers}`);

      // 列出失败的运营商和原因
      const failedCarriers = failedResults.map((r: any) => `${r.carrier}(${r.error || 'unknown'})`).join('、');
      findings.push(`❌ 访问失败: ${failedCarriers}`);

      recommendations.push("部分运营商网络存在问题");
      recommendations.push("可能是DNS解析或网络路由问题");
      recommendations.push("建议检查网络设置或更换DNS服务器");

    } else {
      // 所有运营商都无法访问
      summary = `网站访问异常 - ${url}`;
      findings.push(`❌ 所有${testResults.length}个运营商网络均无法访问`);

      // 分析失败原因
      const errorTypes = failedResults.map((r: any) => r.error || 'unknown');
      const commonErrors = [...new Set(errorTypes)];

      if (commonErrors.length === 1) {
        findings.push(`🔍 统一错误原因: ${commonErrors[0]}`);
      } else {
        findings.push(`🔍 多种错误原因: ${commonErrors.join('、')}`);
      }

      // 根据错误类型给出建议
      if (commonErrors.some(e => e.includes('超时') || e.includes('timeout'))) {
        recommendations.push("网络连接超时，检查网络连接稳定性");
      }
      if (commonErrors.some(e => e.includes('DNS') || e.includes('解析'))) {
        recommendations.push("DNS解析失败，检查DNS设置");
      }
      if (commonErrors.some(e => e.includes('连接') || e.includes('connection'))) {
        recommendations.push("网络连接失败，检查防火墙和网络配置");
      }

      recommendations.push("确认目标网站是否正常运行");
      recommendations.push("尝试使用其他网络或设备进行测试");
    }

  } else {
    // 没有测试结果
    summary = `网站可访问性测试失败 - ${url}`;
    findings.push(`❌ 未能获取有效的测试结果`);
    recommendations.push("检查网络连接");
    recommendations.push("重新执行测试");
  }

  return {
    summary,
    findings,
    recommendations,
    needsNextStep: context.currentStep < context.totalSteps - 1,
    nextStepReason: "继续检查其他网络指标"
  };
}

// 网关信息检测结果评估
function evaluateGatewayInfoResult(result: any, context: any): any {
  console.log('🖥️ 评估网关信息结果:', result);

  const data = result.data || result;
  const gatewayIP = data.gateway_ip || 'unknown';
  const localIP = data.local_ip || 'unknown';
  const networkInterface = data.network_interface || 'unknown';
  const dnsServers = data.dns_servers || [];

  let summary = "网关信息检测完成";
  let findings = [];
  let recommendations = [];

  // 分析网关信息
  if (gatewayIP && gatewayIP !== '未知' && gatewayIP !== 'unknown') {
    summary = `网关信息获取成功 - ${gatewayIP}`;
    findings.push(`✅ 网关地址: ${gatewayIP}`);

    // 分析网关IP类型
    if (gatewayIP.startsWith('192.168.')) {
      findings.push(`🏠 私有网络环境 (192.168.x.x)`);
    } else if (gatewayIP.startsWith('10.')) {
      findings.push(`🏢 企业网络环境 (10.x.x.x)`);
    } else if (gatewayIP.startsWith('172.')) {
      findings.push(`🏢 企业网络环境 (172.x.x.x)`);
    } else {
      findings.push(`🌐 公网网关环境`);
    }
  } else {
    summary = "网关信息获取失败";
    findings.push(`❌ 无法获取网关地址`);
    recommendations.push("检查网络连接状态");
    recommendations.push("确认设备已正确连接到网络");
  }

  // 分析本地IP
  if (localIP && localIP !== '未知' && localIP !== 'unknown') {
    findings.push(`📱 本地IP: ${localIP}`);

    if (localIP.startsWith('169.254.')) {
      findings.push(`⚠️ 检测到APIPA地址，可能存在DHCP问题`);
      recommendations.push("检查DHCP服务器配置");
      recommendations.push("尝试重新连接网络");
    }
  }

  // 分析网络接口
  if (networkInterface && networkInterface !== '未知' && networkInterface !== 'unknown') {
    findings.push(`🔌 网络接口: ${networkInterface}`);

    if (networkInterface.includes('en0') || networkInterface.includes('wlan')) {
      findings.push(`📶 使用WiFi连接`);
    } else if (networkInterface.includes('eth') || networkInterface.includes('en1')) {
      findings.push(`🔗 使用有线连接`);
    }
  }

  // 分析DNS配置
  if (dnsServers.length > 0) {
    findings.push(`🌐 DNS服务器: ${dnsServers.length}个`);

    // 分析DNS服务器类型
    const publicDNS = dnsServers.filter(dns =>
      dns === '8.8.8.8' || dns === '8.8.4.4' ||
      dns === '1.1.1.1' || dns === '1.0.0.1' ||
      dns === '114.114.114.114' || dns === '223.5.5.5'
    );

    const localDNS = dnsServers.filter(dns =>
      dns.startsWith('192.168.') || dns.startsWith('10.') || dns.startsWith('172.')
    );

    if (publicDNS.length > 0) {
      findings.push(`✅ 配置了${publicDNS.length}个公共DNS服务器`);
    }

    if (localDNS.length > 0) {
      findings.push(`🏠 配置了${localDNS.length}个本地DNS服务器`);
    }

    if (dnsServers.length === 1) {
      recommendations.push("建议配置备用DNS服务器以提高可靠性");
    }
  } else {
    findings.push(`⚠️ 未检测到DNS服务器配置`);
    recommendations.push("检查DNS设置");
    recommendations.push("可能影响域名解析功能");
  }

  // 网络配置建议
  if (gatewayIP && localIP && dnsServers.length > 0) {
    findings.push(`🎯 网络配置完整，基础连接正常`);
  } else {
    recommendations.push("网络配置不完整，可能影响网络功能");
  }

  return {
    summary,
    findings,
    recommendations,
    needsNextStep: context.currentStep < context.totalSteps - 1,
    nextStepReason: "继续检查网络连通性和性能"
  };
}

// 备用评估方案
function getFallbackEvaluation(toolId: string, result: any, context: any): any {
  console.log('🔄 使用备用评估方案 - 工具ID:', toolId);

  const toolNames: Record<string, string> = {
    ping: 'Ping测试',
    ping_test: 'Ping测试',
    wifi_scan: 'WiFi扫描',
    connectivity_check: '连通性检查',
    gateway_info: '网关信息检测',
    gateway_info_check: '网关信息检测',
    packet_capture: '数据包分析',
    website_accessibility_test: '网站可访问性测试',
    speed_test: '网络速度测试',
    trace_route: '路由追踪'
  };

  const toolName = toolNames[toolId] || toolId;

  // 根据工具类型提供更具体的备用评估
  switch (toolId) {
    case 'ping':
    case 'ping_test':
      return {
        summary: `${toolName}执行完成`,
        findings: [
          "✅ 已完成网络连通性测试",
          "📊 收集了延迟和丢包数据"
        ],
        recommendations: [
          "查看详细的Ping测试结果",
          "关注丢包率和平均延迟指标"
        ],
        needsNextStep: context.currentStep < context.totalSteps - 1,
        nextStepReason: "继续检查其他网络指标以获得完整诊断"
      };

    case 'wifi_scan':
      return {
        summary: `${toolName}执行完成`,
        findings: [
          "📶 已扫描周边WiFi网络",
          "📊 收集了信号强度和信道信息"
        ],
        recommendations: [
          "查看当前WiFi连接状态",
          "检查是否存在信道干扰",
          "考虑优化WiFi设置"
        ],
        needsNextStep: context.currentStep < context.totalSteps - 1,
        nextStepReason: "继续检查网络连通性"
      };

    case 'connectivity_check':
      return {
        summary: `${toolName}执行完成`,
        findings: [
          "🌐 已测试多个网络连接点",
          "📊 收集了连通性状态数据"
        ],
        recommendations: [
          "查看各项连通性测试结果",
          "关注失败的连接项目",
          "检查DNS和防火墙设置"
        ],
        needsNextStep: context.currentStep < context.totalSteps - 1,
        nextStepReason: "继续深入分析网络问题"
      };

    case 'website_accessibility_test':
      return {
        summary: `${toolName}执行完成`,
        findings: [
          "🌍 已完成多运营商网站可访问性测试",
          "📊 收集了不同网络环境下的访问数据",
          "🔍 分析了响应时间和连接状态"
        ],
        recommendations: [
          "查看各运营商网络的访问结果",
          "对比不同网络环境的性能差异",
          "关注失败的网络连接和错误原因"
        ],
        needsNextStep: context.currentStep < context.totalSteps - 1,
        nextStepReason: "继续检查其他网络指标"
      };

    case 'gateway_info':
    case 'gateway_info_check':
      return {
        summary: `${toolName}执行完成`,
        findings: [
          "🖥️ 已获取网关和网络配置信息",
          "📊 收集了IP地址、接口和DNS配置",
          "🔍 分析了网络环境和连接类型"
        ],
        recommendations: [
          "查看网关地址和本地IP配置",
          "检查DNS服务器设置是否合理",
          "确认网络接口类型和连接状态"
        ],
        needsNextStep: context.currentStep < context.totalSteps - 1,
        nextStepReason: "继续检查网络连通性"
      };

    default:
      return {
        summary: `${toolName}执行完成`,
        findings: [
          "✅ 工具执行成功",
          "📊 已收集相关诊断数据"
        ],
        recommendations: [
          "查看详细的测试结果",
          "分析收集到的网络数据"
        ],
        needsNextStep: context.currentStep < context.totalSteps - 1,
        nextStepReason: "继续后续诊断步骤"
      };
  }
}

// 生成最终诊断总结
async function generateFinalSummary(context: any, aiModel: any): Promise<string> {
  const summaryPrompt = `
作为网络诊断专家，请为完整的诊断过程生成最终总结报告。

原始问题：${context.originalProblem}
执行的工具：
${context.executedTools.map((tool: any, index: number) => 
  `${index + 1}. ${tool.name} - ${tool.timestamp}\n   结果：${JSON.stringify(tool.result, null, 2)}`
).join('\n\n')}

请生成一个专业的诊断总结，包含：
1. 问题综合分析
2. 主要发现
3. 解决建议
4. 预防措施

要求：
- 语言专业但易懂
- 结论明确
- 建议具体可行
- 格式清晰
`;

  const { text } = await generateText({
    model: aiModel,
    prompt: summaryPrompt,
    temperature: 0.3,
  });

  return text;
}

export async function POST(req: NextRequest) {
  try {
    console.log('📝 开始处理步进式诊断请求');
    
    const requestData: StepwiseDiagnosisRequest = await req.json();
    console.log('📝 请求数据:', requestData);

    // 创建AI模型实例
    const aiModel = createAIClient();
    if (!aiModel) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: 'AI配置无效，请检查环境变量' 
        } as StepwiseDiagnosisResponse),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    switch (requestData.action) {
      case 'analyze': {
        // 分析用户问题，生成诊断计划
        const analysis = await analyzeUserProblem(requestData.message, aiModel);
        
        const response: StepwiseDiagnosisResponse = {
          success: true,
          data: {
            type: 'analysis',
            analysis: analysis.analysis,
            reasoning: analysis.reasoning,
            urgency: analysis.urgency,
            totalSteps: analysis.totalSteps,
            currentStep: 0
          }
        };

        // 保存诊断计划到会话（这里简化处理，实际应该保存到数据库）
        global.diagnosticPlan = analysis;
        
        return new Response(JSON.stringify(response), {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      case 'get_next_step': {
        // 获取下一步工具推荐
        const plan = global.diagnosticPlan;
        if (!plan) {
          return new Response(
            JSON.stringify({
              success: false,
              error: '诊断计划丢失，请重新开始'
            } as StepwiseDiagnosisResponse),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }

        const currentStep = requestData.context?.currentStep || 0;
        const nextTool = getNextStepTool(plan, currentStep);

        if (!nextTool) {
          // 所有步骤完成
          const finalSummary = await generateFinalSummary(requestData.context, aiModel);
          
          return new Response(
            JSON.stringify({
              success: true,
              data: {
                type: 'completion',
                isComplete: true,
                finalSummary
              }
            } as StepwiseDiagnosisResponse),
            { headers: { 'Content-Type': 'application/json' } }
          );
        }

        const response: StepwiseDiagnosisResponse = {
          success: true,
          data: {
            type: 'next_step',
            currentStep: currentStep + 1,
            totalSteps: plan.totalSteps,
            nextTool
          }
        };

        return new Response(JSON.stringify(response), {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      case 'evaluate_result': {
        // 评估工具执行结果
        if (!requestData.context || !requestData.toolResult) {
          return new Response(
            JSON.stringify({
              success: false,
              error: '缺少必要的评估数据'
            } as StepwiseDiagnosisResponse),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }

        const evaluation = await evaluateToolResult(
          requestData.toolResult.toolId,
          requestData.toolResult.result,
          requestData.context,
          aiModel
        );

        const response: StepwiseDiagnosisResponse = {
          success: true,
          data: {
            type: 'evaluation',
            evaluation
          }
        };

        return new Response(JSON.stringify(response), {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      default:
        return new Response(
          JSON.stringify({
            success: false,
            error: '未知的操作类型'
          } as StepwiseDiagnosisResponse),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
    }

  } catch (error) {
    console.error('❌ 步进式诊断处理失败:', error);
    
    return new Response(
      JSON.stringify({
        success: false,
        error: `处理失败: ${(error as Error).message}`
      } as StepwiseDiagnosisResponse),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
} 