import { NextRequest } from 'next/server';
import { experimental_createMCPClient, streamText } from 'ai';
import { Experimental_StdioMCPTransport } from 'ai/mcp-stdio';
import { createOpenAI } from '@ai-sdk/openai';

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

    console.log('⚠️ 未检测到有效的AI API密钥');
    return null;
  } catch (error) {
    console.error('❌ 创建AI客户端失败:', error);
    return null;
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log('📝 开始处理 AI SDK v5 + MCP 诊断请求');
    
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

    console.log('🔌 初始化 MCP 客户端...');

    // 初始化多个 MCP 服务器
    const mcpServers = [
      {
        name: 'ping',
        transport: new Experimental_StdioMCPTransport({
          command: 'python',
          args: ['backend/app/mcp/servers/ping_server_fixed.py'],
        }),
      },
      {
        name: 'wifi',
        transport: new Experimental_StdioMCPTransport({
          command: 'python',
          args: ['backend/app/mcp/servers/wifi_server.py'],
        }),
      },
      {
        name: 'connectivity',
        transport: new Experimental_StdioMCPTransport({
          command: 'python',
          args: ['backend/app/mcp/servers/connectivity_server.py'],
        }),
      },
      {
        name: 'gateway',
        transport: new Experimental_StdioMCPTransport({
          command: 'python',
          args: ['backend/app/mcp/servers/gateway_server.py'],
        }),
      },
      {
        name: 'packet_capture',
        transport: new Experimental_StdioMCPTransport({
          command: 'python',
          args: ['backend/app/mcp/servers/packet_capture_server.py'],
        }),
      },
    ];

    // 创建 MCP 客户端并收集所有工具
    const allMcpClients: Awaited<ReturnType<typeof experimental_createMCPClient>>[] = [];
    const allTools: Record<string, any> = {};

    try {
      for (const serverConfig of mcpServers) {
        try {
          console.log(`🔌 连接到 MCP 服务器: ${serverConfig.name}`);
          
          const mcpClient = await experimental_createMCPClient({
            transport: serverConfig.transport,
          });
          
          allMcpClients.push(mcpClient);
          
          // 获取服务器的工具
          const serverTools = await mcpClient.tools();
          
          // 合并工具，添加服务器名称前缀避免冲突
          Object.keys(serverTools).forEach(toolName => {
            const prefixedName = `${serverConfig.name}_${toolName}`;
            allTools[prefixedName] = serverTools[toolName];
          });
          
          console.log(`✅ ${serverConfig.name} 服务器连接成功，工具数量: ${Object.keys(serverTools).length}`);
        } catch (serverError) {
          console.warn(`⚠️ 无法连接到 ${serverConfig.name} 服务器:`, serverError);
          // 继续处理其他服务器，而不是失败
        }
      }

      console.log(`🔧 总共可用工具数量: ${Object.keys(allTools).length}`);
      console.log(`🔧 可用工具列表: ${Object.keys(allTools).join(', ')}`);

      // 构建系统提示
      const systemPrompt = `你是一个专业的网络诊断助手。

可用工具:
${Object.keys(allTools).map(toolName => `- ${toolName}: ${allTools[toolName].description || '网络诊断工具'}`).join('\n')}

**工具使用指南：**
- ping_* 工具：测试网络连通性和延迟
- wifi_* 工具：扫描和分析WiFi网络
- connectivity_* 工具：检查互联网连接状态
- gateway_* 工具：获取网关和路由信息
- packet_capture_* 工具：进行网络数据包分析

**重要提示：**
1. 根据用户问题选择最合适的工具
2. 工具调用失败时，提供备选方案
3. 对结果进行专业分析和解释
4. 使用中文回答

开始诊断时，请首先了解用户的具体网络问题，然后选择合适的工具进行诊断。`;

      console.log('🔄 开始调用 streamText...');
      
      // 使用 AI SDK v5 的 streamText，原生支持 MCP 工具
      const result = await streamText({
        model: aiModel,
        messages,
        system: systemPrompt,
        tools: allTools,
        maxTokens: 1500,
        temperature: 0.7,
        maxSteps: 3, // 允许多步工具调用
        onFinish: async () => {
          // 清理所有 MCP 客户端连接
          console.log('🧹 清理 MCP 客户端连接...');
          for (const client of allMcpClients) {
            try {
              await client.close();
            } catch (error) {
              console.warn('⚠️ 清理客户端连接时出错:', error);
            }
          }
        },
        onError: async (error) => {
          // 错误时也要清理连接
          console.error('❌ streamText 出错，清理连接...', error);
          for (const client of allMcpClients) {
            try {
              await client.close();
            } catch (cleanupError) {
              console.warn('⚠️ 错误清理时出错:', cleanupError);
            }
          }
        },
      });

      console.log('✅ streamText 调用成功');
      return result.toDataStreamResponse();
      
    } catch (mcpError) {
      console.error('❌ MCP 初始化失败:', mcpError);
      
      // 清理已创建的客户端
      for (const client of allMcpClients) {
        try {
          await client.close();
        } catch (error) {
          console.warn('⚠️ 清理客户端时出错:', error);
        }
      }
      
      return new Response(
        JSON.stringify({ 
          error: 'MCP 服务器连接失败', 
          details: (mcpError as Error).message 
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