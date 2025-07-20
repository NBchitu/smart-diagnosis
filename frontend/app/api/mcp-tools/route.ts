import { NextRequest, NextResponse } from 'next/server';

interface MCPCallRequest {
  server_name: string;
  tool_name: string;
  args: Record<string, any>;
  timeout?: number;
}

export async function POST(req: NextRequest) {
  try {
    const { server_name, tool_name, args, timeout }: MCPCallRequest = await req.json();
    
    console.log('🔧 调用MCP工具:', { server_name, tool_name, args });
    
    // 调用后端MCP API
    const response = await fetch(`http://localhost:8000/api/mcp/call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        server_name,
        tool_name,
        args,
        timeout
      }),
    });

    if (response.ok) {
      const result = await response.json();
      console.log('✅ MCP工具调用成功:', result);
      return NextResponse.json(result);
    } else {
      const errorText = await response.text();
      throw new Error(`后端MCP API响应错误: ${response.status} - ${errorText}`);
    }
    
  } catch (error) {
    console.error('❌ MCP工具调用失败:', error);
    
    return NextResponse.json({
      success: false,
      error: 'MCP工具调用失败',
      details: (error as Error)?.message || 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET(req: NextRequest) {
  try {
    console.log('📋 获取MCP可用工具列表');
    
    // 获取可用的MCP工具
    const response = await fetch(`http://localhost:8000/api/ai/tools`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const result = await response.json();
      console.log('✅ 获取MCP工具列表成功');
      return NextResponse.json(result);
    } else {
      const errorText = await response.text();
      throw new Error(`后端MCP API响应错误: ${response.status} - ${errorText}`);
    }
    
  } catch (error) {
    console.error('❌ 获取MCP工具列表失败:', error);
    
    return NextResponse.json({
      success: false,
      error: '获取MCP工具列表失败',
      details: (error as Error)?.message || 'Unknown error'
    }, { status: 500 });
  }
} 