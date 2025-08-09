import { NextRequest, NextResponse } from 'next/server';

interface TracerouteHop {
  hop: number;
  ip: string;
  hostname?: string;
  rtt1?: number;
  rtt2?: number;
  rtt3?: number;
  avg_rtt?: number;
  status: 'success' | 'timeout' | 'error';
}

interface TracerouteResult {
  success: boolean;
  data?: {
    target: string;
    target_ip: string;
    hops: TracerouteHop[];
    total_hops: number;
    max_hops: number;
    test_duration: number;
    timestamp: string;
    summary: {
      successful_hops: number;
      failed_hops: number;
      avg_latency: number;
      max_latency: number;
    };
  };
  error?: string;
  details?: string;
}

export async function POST(request: NextRequest) {
  console.log('🛣️ 开始路由追踪...');
  
  try {
    const body = await request.json();
    let { host, max_hops = 10 } = body;
    
    if (!host) host = 'www.baidu.com';
    // if (!host) {
    //   return NextResponse.json({
    //     success: false,
    //     error: '请提供目标主机地址'
    //   }, { status: 400 });
    // }

    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/traceroute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        target:host,
        max_hops
      }),
      // 路由追踪可能需要较长时间
      signal: AbortSignal.timeout(90000) // 90秒超时
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result: TracerouteResult = await response.json();
    
    if (result.success) {
      console.log('✅ 路由追踪完成:', {
        target: result.data?.target,
        total_hops: result.data?.total_hops,
        successful_hops: result.data?.summary.successful_hops
      });
    } else {
      console.log('❌ 路由追踪失败:', result.error);
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ 路由追踪API错误:', error);
    
    return NextResponse.json({
      success: false,
      error: '路由追踪失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
