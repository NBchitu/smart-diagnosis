import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { openai, createOpenAI } from '@ai-sdk/openai';
import { aiConfig, getCurrentAIConfig, validateAIConfig } from '@/config/ai.config';

// 模拟的网络诊断工具
const networkTools = {
  ping_test: {
    description: '执行 ping 测试检查网络连通性和延迟',
    parameters: {
      type: 'object',
      properties: {
        host: { type: 'string', description: '要测试的主机地址' },
        count: { type: 'number', description: '测试次数，默认为4' }
      },
      required: ['host']
    }
  },
  speed_test: {
    description: '执行网络速度测试',
    parameters: {
      type: 'object',
      properties: {
        server_id: { type: 'string', description: '指定测试服务器ID' }
      }
    }
  },
  wifi_scan: {
    description: '扫描周边WiFi网络信号',
    parameters: {
      type: 'object',
      properties: {
        interface: { type: 'string', description: '网络接口名称，默认为wlan0' }
      }
    }
  },
  signal_analysis: {
    description: '分析当前WiFi信号质量',
    parameters: {
      type: 'object',
      properties: {
        interface: { type: 'string', description: '网络接口名称' }
      }
    }
  },
  trace_route: {
    description: '追踪网络路径和节点',
    parameters: {
      type: 'object',
      properties: {
        destination: { type: 'string', description: '目标地址' }
      },
      required: ['destination']
    }
  }
};

// 真实的ping工具实现
async function executePingTool(parameters: Record<string, unknown>) {
  try {
    const { host = 'baidu.com', count = 4 } = parameters;
    
    // 调用后端ping API
    const response = await fetch(`http://localhost:8000/api/network/ping_test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ host, count }),
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`Backend ping failed: ${response.status}`);
    }
  } catch (error) {
    console.error('真实ping工具调用失败，使用模拟数据:', error);
    
    // 降级到模拟ping结果
    return {
      host: parameters.host || 'baidu.com',
      packets_sent: parameters.count || 4,
      packets_received: 4,
      packet_loss: '0%',
      avg_latency: '23ms',
      min_latency: '20ms',
      max_latency: '28ms',
      status: 'success',
      fallback: true // 标记这是降级数据
    };
  }
}

async function callNetworkTool(toolName: string, parameters: Record<string, unknown>) {
  try {
    // ping工具使用真实实现
    if (toolName === 'ping_test') {
      return await executePingTool(parameters);
    }

    // 确定工具类型和端点
    let serverType = 'network';
    let apiEndpoint = `http://localhost:8000/api/network/${toolName}`;

    // Sequential Thinking 工具路由到AI端点
    if (['analyze_network_problem', 'generate_diagnostic_sequence', 'evaluate_diagnostic_results'].includes(toolName)) {
      serverType = 'ai';
      apiEndpoint = `http://localhost:8000/api/ai/${toolName}`;
    }

    // 新的网络诊断工具路由到专门的端点
    if (['network_interfaces', 'dns_lookup'].includes(toolName)) {
      serverType = 'network_diagnostic';
      apiEndpoint = `http://localhost:8000/api/network_diagnostic/${toolName}`;
    }

    // 调用后端 API
    const response = await fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(parameters),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error calling ${toolName}:`, error);
    // 返回模拟数据作为降级方案
    return getMockToolResult(toolName, parameters);
  }
}

function getMockToolResult(toolName: string, parameters: Record<string, unknown>) {
  const mockResults: Record<string, Record<string, unknown>> = {
    ping_test: {
      host: parameters.host || 'baidu.com',
      packets_sent: parameters.count || 4,
      packets_received: 4,
      packet_loss: '0%',
      avg_latency: '23ms',
      min_latency: '20ms',
      max_latency: '28ms',
      status: 'success'
    },
    speed_test: {
      download_speed: 45.2,
      upload_speed: 12.8,
      ping: 23,
      server: '北京电信',
      jitter: 2.1,
      status: 'success'
    },
    wifi_scan: {
      networks: [
        { ssid: 'WiFi-Home-5G', signal_strength: -35, frequency: '5GHz', channel: 36, encryption: 'WPA3' },
        { ssid: 'WiFi-Home-2.4G', signal_strength: -42, frequency: '2.4GHz', channel: 6, encryption: 'WPA2' },
        { ssid: 'TP-LINK_123', signal_strength: -65, frequency: '2.4GHz', channel: 11, encryption: 'WPA2' },
        { ssid: 'ChinaNet-456', signal_strength: -72, frequency: '5GHz', channel: 149, encryption: 'WPA2' }
      ],
      scan_time: new Date().toISOString(),
      status: 'success'
    },
    signal_analysis: {
      current_network: 'WiFi-Home-5G',
      signal_strength: -35,
      signal_quality: 85,
      noise_level: -95,
      snr: 60,
      channel: 36,
      frequency: '5GHz',
      bandwidth: '80MHz',
      tx_rate: '866Mbps',
      rx_rate: '866Mbps',
      status: 'success'
    },
    trace_route: {
      destination: parameters.destination,
      hops: [
        { hop: 1, ip: '192.168.1.1', hostname: 'router.local', latency: '1ms' },
        { hop: 2, ip: '10.0.0.1', hostname: 'isp-gateway', latency: '12ms' },
        { hop: 3, ip: '220.181.38.148', hostname: 'baidu.com', latency: '23ms' }
      ],
      total_hops: 3,
      status: 'success'
    },
    analyze_network_problem: {
      success: true,
      analysis: {
        problem_type: 'connectivity',
        priority: parameters.priority || 'medium',
        impact_assessment: {
          overall_impact: 'medium',
          business_impact: 'medium',
          user_impact: 'low',
          system_impact: 'medium'
        },
        estimated_resolution_time: {
          estimated_minutes: 30,
          range: { min: 20, max: 45 },
          confidence: 'medium'
        },
        troubleshooting_steps: [
          {
            step: 1,
            title: '问题确认',
            description: '确认问题现象和影响范围',
            estimated_time: 5
          },
          {
            step: 2,
            title: '基础连通性测试',
            description: '测试到网关和外网的连通性',
            estimated_time: 10
          }
        ],
        recommended_tools: [
          { name: 'ping', priority: 'high', description: '测试网络连通性' },
          { name: 'traceroute', priority: 'high', description: '追踪网络路径' }
        ],
        key_focus_areas: ['网络连通性', '路由配置', '防火墙设置']
      },
      metadata: {
        analysis_time: new Date().toISOString(),
        confidence_score: 0.85,
        complexity_level: 'medium'
      }
    },
    generate_diagnostic_sequence: {
      success: true,
      diagnostic_sequence: [
        {
          name: 'ping_gateway',
          description: '测试网关连通性',
          tool: 'ping',
          critical: true,
          importance: 'critical',
          estimated_duration: 5
        },
        {
          name: 'ping_dns',
          description: '测试DNS服务器',
          tool: 'ping',
          critical: true,
          importance: 'high',
          estimated_duration: 5
        }
      ],
      total_steps: 2,
      estimated_total_time: 10,
      critical_steps: 1
    },
    evaluate_diagnostic_results: {
      success: true,
      evaluation: {
        root_cause: {
          primary_cause: 'connectivity_failure',
          contributing_factors: ['网络配置错误', '硬件故障'],
          confidence: 'high'
        },
        confidence_level: 'high',
        solutions: [
          { solution: '检查网络配置', priority: 'high', effort: 'low' },
          { solution: '重启网络设备', priority: 'high', effort: 'low' }
        ],
        solution_feasibility: {
          high_feasibility: [
            { solution: '检查网络配置', priority: 'high', effort: 'low' }
          ]
        },
        next_actions: [
          {
            action: '检查网络配置',
            timeline: 'immediate',
            owner: 'network_admin',
            dependencies: []
          }
        ],
        resolution_likelihood: 0.8
      },
      summary: {
        key_findings: ['网络连通性异常'],
        critical_issues: ['ping测试失败'],
        recommended_priority: 'high'
      }
    },
    network_interfaces: {
      success: true,
      interfaces: [
        {
          name: 'eth0',
          addresses: [
            { type: 'IPv4', address: '192.168.1.100' },
            { type: 'IPv6', address: 'fe80::1' }
          ],
          status: 'up'
        },
        {
          name: 'wlan0',
          addresses: [
            { type: 'IPv4', address: '192.168.1.101' }
          ],
          status: 'up'
        }
      ],
      total_interfaces: 2,
      system: 'linux'
    },
    dns_lookup: {
      success: true,
      domain: parameters.domain || 'example.com',
      record_type: parameters.record_type || 'A',
      records: [
        { type: 'A', value: '93.184.216.34' }
      ],
      canonical_name: parameters.domain || 'example.com',
      query_time: 23
    }
  };

  return mockResults[toolName] || { error: 'Unknown tool', status: 'error' };
}

// 创建AI客户端
function createAIClient() {
  try {
    // 从环境变量获取配置
    const provider = process.env.AI_PROVIDER || 'openrouter';
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    console.log('AI客户端配置检查:', {
      provider,
      openRouterKey: openRouterKey ? `set (${openRouterKey.length} chars)` : 'not set',
      openAIKey: openAIKey ? `set (${openAIKey.length} chars)` : 'not set'
    });
    
    // 根据配置选择API
    if (provider === 'openrouter' && openRouterKey && openRouterKey.length > 10) {
      const client = createOpenAI({
        baseURL: 'https://openrouter.ai/api/v1',
        apiKey: openRouterKey,
      });
      const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-3-sonnet';
      console.log(`✅ 使用OpenRouter AI模型: ${model}`);
      return client(model);
    }
    
    if (provider === 'openai' && openAIKey && openAIKey.startsWith('sk-')) {
      const client = createOpenAI({
        baseURL: 'https://api.openai.com/v1',
        apiKey: openAIKey,
      });
      const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
      console.log(`✅ 使用OpenAI模型: ${model}`);
      return client(model);
    }

    // 如果没有配置真实API密钥，使用模拟客户端
    console.log('⚠️ 未检测到有效的AI API密钥，使用模拟AI客户端进行工具调用演示');
    console.log('请在 .env.local 文件中配置 OPENROUTER_API_KEY 或 OPENAI_API_KEY');
    return null;

  } catch (error) {
    console.error('❌ 创建AI客户端失败:', error);
    return null;
  }
}


// 模拟AI回答（降级方案）
function generateMockAIResponse(userMessage: string): string {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('慢') || lowerMessage.includes('卡')) {
    return `我理解您的网络速度问题。让我为您进行诊断：

**可能的原因：**
1. 网络带宽不足
2. WiFi信号质量差
3. 路由器性能问题
4. 网络拥塞

**建议的解决方案：**
1. 重启路由器和设备
2. 检查WiFi信号强度
3. 更换到5G频段
4. 联系运营商检查线路

您可以尝试这些步骤，如果问题持续，我建议进行详细的网络检测。`;
  }
  
  if (lowerMessage.includes('连不上') || lowerMessage.includes('断线')) {
    return `网络连接问题分析：

**常见原因：**
1. WiFi密码错误
2. 路由器故障
3. 网络配置问题
4. 设备驱动问题

**解决步骤：**
1. 检查WiFi密码是否正确
2. 重启路由器等待2分钟
3. 检查网线连接
4. 重置网络设置

如果以上步骤无效，建议检查路由器指示灯状态。`;
  }
  
  return `感谢您的咨询。我是网络诊断助手，可以帮您解决网络问题。

**我可以协助：**
- 网络速度慢的问题
- 连接不稳定的故障
- WiFi信号弱的优化
- 网络配置的建议

请详细描述您遇到的具体问题，我会为您提供针对性的解决方案。

注意：当前AI服务配置不完整，正在使用基础诊断模式。`;
}

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    // 创建AI模型实例
    const aiModel = createAIClient();

    // 如果AI配置无效，使用降级方案（包含工具调用演示）
    if (!aiModel) {
      const userMessage = messages[messages.length - 1]?.content || '';
      
      // 检查是否需要调用ping工具
      const shouldUsePing = userMessage.includes('连接') || userMessage.includes('连不上') || 
                           userMessage.includes('无法访问') || userMessage.includes('打不开');
      
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          setTimeout(async () => {
            if (shouldUsePing) {
              // 模拟AI调用ping工具的过程
              const steps = [
                '我来帮您诊断网络连接问题。首先让我测试一下到百度的连通性。',
                '\n\n🔧 **正在执行ping测试...**',
                ''
              ];
              
              // 逐步发送响应
              for (const step of steps) {
                if (step) {
                  controller.enqueue(encoder.encode(`0:"${step.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"\n`));
                  await new Promise(resolve => setTimeout(resolve, 300));
                }
              }
              
              // 调用真实的ping工具
              try {
                const pingResult = await executePingTool({ host: 'baidu.com', count: 4 });
                
                let analysis = `\n✅ **Ping测试结果分析：**\n- 目标主机：${pingResult.host || pingResult.data?.host || 'baidu.com'}\n- 发送数据包：${pingResult.packets_sent || pingResult.data?.packets_sent}个\n- 接收数据包：${pingResult.packets_received || pingResult.data?.packets_received}个\n- 丢包率：${pingResult.packet_loss || pingResult.data?.packet_loss}\n- 平均延迟：${pingResult.avg_latency || pingResult.data?.avg_latency}\n\n`;
                
                const isSuccess = (pingResult.status === 'success' && !pingResult.fallback) || 
                                 (pingResult.data && pingResult.data.packet_loss === '0.0%');
                
                if (isSuccess) {
                  analysis += '**诊断结论：** 网络连接正常，ping测试成功。问题可能出现在：\n1. DNS解析问题\n2. 防火墙或代理设置\n3. 浏览器缓存问题\n4. 特定端口被封锁\n\n**建议解决方案：**\n1. 清理浏览器缓存和Cookie\n2. 尝试使用不同的DNS服务器（如8.8.8.8）\n3. 检查防火墙和安全软件设置\n4. 尝试使用其他浏览器或设备测试';
                } else {
                  analysis += '**诊断结论：** 检测到网络连接问题。\n\n**建议解决方案：**\n1. 检查网络线缆连接\n2. 重启路由器和调制解调器\n3. 联系网络服务提供商检查线路\n4. 检查网络设备是否过热';
                }
                
                controller.enqueue(encoder.encode(`0:"${analysis.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"\n`));
              } catch (error) {
                const fallbackMsg = '\n⚠️ **Ping测试遇到问题，基于经验给出建议：**\n\n建议按以下步骤排查：\n1. 检查网线或WiFi连接\n2. 重启网络设备\n3. 手动设置DNS为8.8.8.8\n4. 联系网络服务商确认线路状态';
                controller.enqueue(encoder.encode(`0:"${fallbackMsg.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"\n`));
              }
            } else {
              // 普通问题处理
              const mockResponse = generateMockAIResponse(userMessage);
              controller.enqueue(encoder.encode(`0:"${mockResponse.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"\n`));
            }
            
            // 发送完成标记
            setTimeout(() => {
              controller.enqueue(encoder.encode('d:{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":200}}\n'));
              controller.close();
            }, 200);
          }, 300);
        }
      });

      return new Response(stream, {
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    console.log('🔄 开始调用streamText，AI模型:', aiModel);
    
    // 检查用户消息是否需要ping工具
    const userMessage = messages[messages.length - 1]?.content || '';
    const needsPing = userMessage.includes('连接') || userMessage.includes('连不上') || 
                     userMessage.includes('无法访问') || userMessage.includes('打不开') ||
                     userMessage.includes('断线') || userMessage.includes('网络');
    
    // 暂时移除工具配置，确保基本AI功能正常
    // 为用户提供详细的网络诊断建议，并承诺执行ping测试
    const result = await streamText({
      model: aiModel!,
      messages,
      system: `你是一个专业的网络诊断助手。请根据用户描述的网络问题提供详细的诊断和解决方案。

对于网络连接问题，请包括：
1. 可能原因分析
2. 详细排查步骤
3. 具体解决方案
4. 预防措施建议

如果用户提到连接、断线等问题，请建议进行ping测试来验证网络连通性。`,
      maxTokens: 500
    });

    console.log('✅ streamText调用成功');
    return result.toDataStreamResponse();
  } catch (error: any) {
    console.error('Error in AI diagnosis API:', error);
    console.error('Error details:', {
      message: error?.message || 'Unknown error',
      stack: error?.stack || 'No stack trace',
      envVars: {
        AI_PROVIDER: process.env.AI_PROVIDER,
        OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY ? 'set' : 'not set',
        OPENROUTER_MODEL: process.env.OPENROUTER_MODEL
      }
    });
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        details: process.env.NODE_ENV === 'development' ? error?.message || 'Unknown error' : undefined 
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 