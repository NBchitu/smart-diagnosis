import { NextRequest } from 'next/server';
import { streamText, tool } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import { z } from 'zod';

// 调用MCP工具的函数
async function callMCPTool(serverName: string, toolName: string, args: Record<string, any>) {
  try {
    console.log(`🔧 调用MCP工具: ${serverName}.${toolName}`, args);
    
    const response = await fetch(`http://localhost:8000/api/mcp/call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        server_name: serverName,
        tool_name: toolName,
        args: args,
      }),
    });

    if (!response.ok) {
      throw new Error(`MCP API调用失败: ${response.status}`);
    }

    const result = await response.json();
    console.log(`✅ MCP工具调用成功: ${serverName}.${toolName}`, result);
    
    return result;
  } catch (error) {
    console.error(`❌ MCP工具调用失败: ${serverName}.${toolName}`, error);
    throw error;
  }
}

// 创建AI客户端
function createAIClient() {
  try {
    const provider = process.env.AI_PROVIDER || 'openrouter';
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    console.log('AI客户端配置检查:', {
      provider,
      openRouterKey: openRouterKey ? `set (${openRouterKey.length} chars)` : 'not set',
      openAIKey: openAIKey ? `set (${openAIKey.length} chars)` : 'not set'
    });
    
    if (provider === 'openrouter' && openRouterKey && openRouterKey.length > 10) {
      const client = createOpenAI({
        baseURL:  process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
        apiKey: openRouterKey,
      });
      const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku';
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

    console.log('⚠️ 未检测到有效的AI API密钥');
    return null;

  } catch (error) {
    console.error('❌ 创建AI客户端失败:', error);
    return null;
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log('📝 开始处理MCP集成AI诊断请求');
    
    const { messages } = await req.json();
    console.log('📝 接收到消息:', messages);

    // 创建AI模型实例
    console.log('🤖 创建AI客户端...');
    const aiModel = createAIClient();
    if (!aiModel) {
      console.error('❌ AI客户端创建失败');
      return new Response(
        JSON.stringify({ error: 'AI配置无效，请检查环境变量' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // 使用标准AI SDK工具格式定义MCP工具
    const tools = {
      // Ping 工具
      pingHost: tool({
        description: 'Ping指定主机检测网络连通性',
        parameters: z.object({
          host: z.string().describe('要测试的主机地址').default('baidu.com'),
          count: z.number().describe('测试次数').default(4).optional(),
          timeout: z.number().describe('超时时间(秒)').default(10).optional()
        }),
        execute: async ({ host, count = 4, timeout = 10 }) => {
          try {
            const result = await callMCPTool('ping', 'ping_host', {
              host,
              count,
              timeout
            });
            return result;
          } catch (error) {
            return {
              success: false,
              error: `ping测试失败: ${(error as Error).message}`,
              host
            };
          }
        }
      }),

      // WiFi 扫描工具
      scanWifi: tool({
        description: '扫描周围的WiFi网络',
        parameters: z.object({}),
        execute: async () => {
          try {
            const result = await callMCPTool('wifi', 'scan_wifi_networks', {});
            return result;
          } catch (error) {
            return {
              success: false,
              error: `WiFi扫描失败: ${(error as Error).message}`
            };
          }
        }
      }),

      // 网络连通性检查工具
      checkConnectivity: tool({
        description: '检查互联网连通性',
        parameters: z.object({
          testHosts: z.array(z.string()).describe('测试主机列表').optional(),
          timeout: z.number().describe('超时时间(秒)').default(10).optional()
        }),
        execute: async ({ testHosts, timeout = 10 }) => {
          try {
            const result = await callMCPTool('connectivity', 'check_internet_connectivity', {
              test_hosts: testHosts,
              timeout
            });
            return result;
          } catch (error) {
            return {
              success: false,
              error: `连通性检查失败: ${(error as Error).message}`
            };
          }
        }
      }),

      // 网关信息获取工具
      getGatewayInfo: tool({
        description: '获取网关信息',
        parameters: z.object({}),
        execute: async () => {
          try {
            const result = await callMCPTool('gateway', 'get_default_gateway', {});
            return result;
          } catch (error) {
            return {
              success: false,
              error: `获取网关信息失败: ${(error as Error).message}`
            };
          }
        }
      }),

      // 智能抓包分析工具
      startPacketCapture: tool({
        description: '开始智能网络抓包分析，专注于网络问题诊断',
        parameters: z.object({
          target: z.string().describe('抓包目标：域名、IP地址或端口号'),
          mode: z.string().describe('抓包模式：domain、port、web、diagnosis、auto').default('auto').optional(),
          duration: z.number().describe('抓包持续时间（秒）').default(30).optional(),
          interface: z.string().describe('网络接口，留空自动检测').optional()
        }),
        execute: async ({ target, mode = 'auto', duration = 30, interface: iface }) => {
          try {
            const result = await callMCPTool('packet_capture', 'start_packet_capture', {
              target,
              mode,
              duration,
              interface: iface
            });
            return result;
          } catch (error) {
            return {
              success: false,
              error: `抓包分析失败: ${(error as Error).message}`,
              target
            };
          }
        }
      }),

      // 获取抓包状态工具
      getPacketCaptureStatus: tool({
        description: '获取当前抓包状态和已分析的数据包信息',
        parameters: z.object({}),
        execute: async () => {
          try {
            const result = await callMCPTool('packet_capture', 'get_capture_status', {});
            return result;
          } catch (error) {
            return {
              success: false,
              error: `获取抓包状态失败: ${(error as Error).message}`
            };
          }
        }
      }),

      // 停止抓包工具
      stopPacketCapture: tool({
        description: '停止当前的抓包任务',
        parameters: z.object({}),
        execute: async () => {
          try {
            const result = await callMCPTool('packet_capture', 'stop_packet_capture', {});
            return result;
          } catch (error) {
            return {
              success: false,
              error: `停止抓包失败: ${(error as Error).message}`
            };
          }
        }
      }),

      // 列出网络接口工具
      listNetworkInterfaces: tool({
        description: '列出所有可用的网络接口',
        parameters: z.object({}),
        execute: async () => {
          try {
            const result = await callMCPTool('packet_capture', 'list_network_interfaces', {});
            return result;
          } catch (error) {
            return {
              success: false,
              error: `获取网络接口列表失败: ${(error as Error).message}`
            };
          }
        }
      })
    };

    console.log('🔧 可用的AI SDK工具:', Object.keys(tools));

    // 构建系统提示
    const systemPrompt = `你是一个专业的网络诊断助手。

可用工具:
- pingHost: 测试指定主机的网络连通性和延迟
- scanWifi: 扫描周围的WiFi网络
- checkConnectivity: 检查互联网连通性
- getGatewayInfo: 获取网关信息
- startPacketCapture: 开始智能网络抓包分析（合法的网络诊断工具）
- getPacketCaptureStatus: 获取抓包状态和分析结果
- stopPacketCapture: 停止抓包任务
- listNetworkInterfaces: 列出可用网络接口

**关于抓包分析：**
网络抓包分析是完全合法且必要的网络诊断技术，用于：
- 分析网络连接问题
- 诊断应用程序网络故障
- 检测网络性能问题
- 排查DNS解析问题
- 分析特定网站或服务的连接状况

当用户遇到网络问题时，抓包分析是重要的诊断手段，可以帮助发现问题根源。

**抓包工具使用指南：**
- 当用户说"抓包"、"分析流量"、"检查网络流量"时，使用 startPacketCapture
- 当用户说"停止抓包"、"结束抓包"、"停止分析"时，使用 stopPacketCapture
- 当用户询问"抓包状态"、"抓包进度"、"抓包结果"时，使用 getPacketCaptureStatus
- 当需要了解网络接口时，使用 listNetworkInterfaces

**抓包工作流程（重要异步流程）：**
1. 用户请求抓包 → 调用 startPacketCapture → 返回启动状态（running）
2. 前端检测到启动 → 开始轮询状态检查
3. 用户要求停止 → 调用 stopPacketCapture → 返回停止确认
4. 需要查看状态/结果 → 调用 getPacketCaptureStatus → 返回实时状态或最终结果

**重要：工具调用响应格式严格规则：**

**对于ping测试，在工具调用后，请按此格式回复：**

根据ping测试结果，[分析网络状况]...

\`\`\`json
{
  "type": "ping_result",
  "data": {
    "host": "实际主机名",
    "success": true/false,
    "packets_transmitted": 发送包数,
    "packets_received": 接收包数,
    "packet_loss": 丢包率,
    "min_time": 最小延迟,
    "max_time": 最大延迟,
    "avg_time": 平均延迟,
    "times": [每次延迟数组],
    "output": "原始输出",
    "error": "错误信息",
    "return_code": 返回码
  }
}
\`\`\`

**对于启动抓包 (startPacketCapture)，只返回启动确认状态：**

抓包任务已启动，正在捕获网络数据包...

\`\`\`json
{
  "type": "packet_capture_started",
  "data": {
    "session_id": "启动返回的真实session_id",
    "target": "抓包目标",
    "mode": "抓包模式",
    "duration": 抓包时长,
    "interface": "网络接口",
    "status": "running",
    "message": "抓包已启动",
    "start_time": "开始时间"
  }
}
\`\`\`

**对于抓包状态查询 (getPacketCaptureStatus)，根据实际状态响应：**

如果抓包正在进行中：
当前抓包状态：正在进行中，已捕获 X 个数据包...

\`\`\`json
{
  "type": "packet_capture_status",
  "data": {
    "session_id": "真实session_id",
    "is_capturing": true,
    "current_packet_count": 当前包数量,
    "elapsed_time": 已用时间,
    "remaining_time": 剩余时间,
    "status": "running",
    "target": "目标",
    "filter": "过滤条件"
  }
}
\`\`\`

如果抓包已完成且有分析结果：
抓包分析已完成，检测到以下网络状况...

\`\`\`json
{
  "type": "packet_capture_result",
  "data": {
    "session_id": "真实session_id",
    "target": "抓包目标",
    "mode": "抓包模式",
    "status": "completed",
    "duration": 实际时长,
    "packets_captured": 实际包数量,
    "interface": "网络接口",
    "start_time": "开始时间",
    "analysis": 从工具返回的真实分析数据,
    "recommendations": 从工具返回的真实建议,
    "saved_files": 保存的文件列表,
    "error": null
  }
}
\`\`\`

**对于停止抓包 (stopPacketCapture)：**

抓包任务已停止...

\`\`\`json
{
  "type": "packet_capture_stopped",
  "data": {
    "session_id": "真实session_id",
    "message": "停止消息",
    "final_packet_count": 最终包数量,
    "total_duration": 总时长,
    "status": "stopped",
    "saved_files": 保存的文件列表
  }
}
\`\`\`

**关键注意事项：**
- 绝对不能在startPacketCapture后立即返回详细分析结果
- 必须使用工具返回的真实数据，不能编造任何数值
- startPacketCapture只返回启动状态，分析结果只能通过getPacketCaptureStatus获取
- 所有数据必须来自工具的实际返回结果

使用中文回答。`;

    console.log('🔄 开始调用streamText with MCP工具...');
    
    try {
      // 使用标准AI SDK工具格式调用streamText
      const result = await streamText({
        model: aiModel,
        messages,
        system: systemPrompt,
        tools: tools,
        maxTokens: 1500,
        temperature: 0.7,
        maxSteps: 3  // 允许多步对话：工具调用 + 分析生成
      });

      console.log('✅ streamText调用成功');
      return result.toDataStreamResponse();
    } catch (streamError) {
      console.error('❌ streamText调用失败:', streamError);
      return new Response(
        JSON.stringify({ 
          error: 'AI流式处理失败', 
          details: (streamError as Error).message,
          stack: (streamError as Error).stack 
        }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
  } catch (error) {
    console.error('❌ AI诊断API总体错误:', error);
    console.error('错误详情:', {
      message: (error as Error)?.message,
      stack: (error as Error)?.stack
    });
    
    return new Response(
      JSON.stringify({ 
        error: '内部服务器错误',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 