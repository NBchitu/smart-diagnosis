import { NextRequest, NextResponse } from 'next/server';

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

export async function GET(req: NextRequest) {
  try {
    console.log('🔄 获取抓包状态...');
    
    // 从URL参数中获取session_id
    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get('session_id');
    
    console.log('📋 查询参数:', { sessionId });
    
    // 调用MCP获取抓包状态，如果有session_id就传递
    const args = sessionId ? { session_id: sessionId } : {};
    const result = await callMCPTool('packet_capture', 'get_capture_status', args);
    
    if (!result.success) {
      return NextResponse.json({
        success: false,
        error: result.error || '获取抓包状态失败'
      }, { status: 400 });
    }

    const statusData = result.data;
    console.log('📊 抓包状态数据:', {
      session_id: statusData.session_id,
      status: statusData.status,
      is_capturing: statusData.is_capturing,
      current_packet_count: statusData.current_packet_count,
      elapsed_time: statusData.elapsed_time,
      remaining_time: statusData.remaining_time
    });

    return NextResponse.json({
      success: true,
      data: statusData
    });

  } catch (error) {
    console.error('❌ 获取抓包状态错误:', error);
    return NextResponse.json({
      success: false,
      error: '服务器内部错误',
      details: (error as Error).message
    }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const { action, session_id } = await req.json();
    
    if (action === 'stop') {
      console.log('⏹️ 停止抓包任务...', { session_id });
      
      // 调用MCP停止抓包，如果有session_id则传递
      const args = session_id ? { session_id } : {};
      const result = await callMCPTool('packet_capture', 'stop_packet_capture', args);
      
      if (!result.success) {
        return NextResponse.json({
          success: false,
          error: result.error || '停止抓包失败'
        }, { status: 400 });
      }

      return NextResponse.json({
        success: true,
        data: result.data,
        message: '抓包任务已停止'
      });
    }

    return NextResponse.json({
      success: false,
      error: '不支持的操作'
    }, { status: 400 });

  } catch (error) {
    console.error('❌ 抓包控制错误:', error);
    return NextResponse.json({
      success: false,
      error: '服务器内部错误',
      details: (error as Error).message
    }, { status: 500 });
  }
} 