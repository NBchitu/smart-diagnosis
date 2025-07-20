import { NextRequest, NextResponse } from 'next/server';
import { openai } from '@ai-sdk/openai';
import { createOpenAI } from '@ai-sdk/openai';
import { generateText } from 'ai';

// 调用MCP工具的辅助函数
async function callMCPTool(serverName: string, toolName: string, args: Record<string, any>) {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const mcpUrl = `${baseUrl}/api/mcp/call`;
    
    console.log(`🔧 调用MCP工具: ${serverName}.${toolName}`, args);
    
    const response = await fetch(mcpUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        server_name: serverName,
        tool_name: toolName,
        args: args
      })
    });

    if (!response.ok) {
      throw new Error(`MCP调用失败: ${response.status} ${response.statusText}`);
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
  const provider = process.env.NEXT_PUBLIC_AI_PROVIDER || 'openrouter';
  
  if (provider === 'openrouter') {
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    if (!openRouterKey) {
      throw new Error('OPENROUTER_API_KEY 环境变量未设置');
    }

    const client = createOpenAI({
      baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      apiKey: openRouterKey,
    });

    return client(process.env.OPENROUTER_MODEL_SUMMARY||'deepseek/deepseek-chat');
  }
  
  throw new Error(`不支持的AI提供商: ${provider}`);
}

export async function POST(req: NextRequest) {
  try {
    const { session_id } = await req.json();
    
    if (!session_id) {
      return NextResponse.json({
        success: false,
        error: '缺少session_id参数'
      }, { status: 400 });
    }

    console.log('🧠 开始自动分析抓包结果...', session_id);
    
    // 1. 获取抓包状态和结果
    const statusResult = await callMCPTool('packet_capture', 'get_capture_status', {});
    
    if (!statusResult.success) {
      return NextResponse.json({
        success: false,
        error: '无法获取抓包状态'
      }, { status: 400 });
    }

    const captureData = statusResult.data;
    console.log('📊 抓包数据:', captureData);

    // 2. 构建分析提示
    const analysisPrompt = `请对以下网络抓包数据进行专业分析：

抓包会话信息：
- 会话ID: ${captureData.session_id || session_id}
- 抓包目标: ${captureData.target || '未知'}
- 抓包模式: ${captureData.mode || '未知'}
- 抓包时长: ${captureData.duration || '未知'}秒
- 捕获包数: ${captureData.packets_captured || 0}个
- 网络接口: ${captureData.interface || '未知'}
- 抓包状态: ${captureData.status || '未知'}

抓包结果数据：
${JSON.stringify(captureData, null, 2)}

请按以下要求进行分析：

1. **网络连接质量评估**
   - 分析协议分布是否正常
   - 评估连接成功率和响应时间
   - 识别可能的性能瓶颈

2. **问题检测和诊断**
   - 识别异常的网络行为
   - 检测连接超时、重试、错误等问题
   - 分析DNS解析和HTTP请求状态

3. **性能优化建议**
   - 基于抓包结果提供具体的优化建议
   - 识别可能的网络配置问题
   - 建议改进措施

4. **总结和评级**
   - 给出网络状况的整体评级（优秀/良好/一般/较差/很差）
   - 总结主要发现和关键问题
   - 提供下一步行动建议

请用中文回答，并提供专业但易懂的分析结果。`;

    // 3. 使用AI进行分析
    const aiModel = createAIClient();
    
    const analysisResult = await generateText({
      model: aiModel,
      prompt: analysisPrompt,
      maxTokens: 2000,
      temperature: 0.3
    });

    console.log('✅ AI分析完成');

    // 4. 构建结构化的分析结果
    const analysisResponse = {
      session_id: captureData.session_id || session_id,
      target: captureData.target,
      mode: captureData.mode,
      status: 'completed',
      duration: captureData.duration,
      packets_captured: captureData.packets_captured,
      interface: captureData.interface,
      start_time: captureData.start_time,
      analysis: {
        summary: {
          total_packets: captureData.packets_captured || 0,
          protocols: captureData.analysis?.summary?.protocols || {},
          top_sources: captureData.analysis?.summary?.top_sources || {},
          top_destinations: captureData.analysis?.summary?.top_destinations || {}
        },
        connections: captureData.analysis?.connections || [],
        dns_queries: captureData.analysis?.dns_queries || [],
        http_requests: captureData.analysis?.http_requests || [],
        problems_detected: captureData.analysis?.problems_detected || []
      },
      recommendations: captureData.recommendations || [],
      ai_analysis: analysisResult.text,
      error: captureData.error
    };

    return NextResponse.json({
      success: true,
      data: analysisResponse,
      message: '抓包结果分析完成'
    });

  } catch (error) {
    console.error('❌ 抓包结果分析错误:', error);
    return NextResponse.json({
      success: false,
      error: '分析失败',
      details: (error as Error).message
    }, { status: 500 });
  }
} 