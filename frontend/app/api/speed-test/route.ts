import { NextRequest, NextResponse } from 'next/server';

interface SpeedTestResult {
  success: boolean;
  data?: {
    download_speed: number;
    upload_speed: number;
    ping: number;
    jitter: number;
    server_info: {
      name: string;
      location: string;
      distance: number;
    };
    test_duration: number;
    timestamp: string;
    isp: string;
    external_ip: string;
  };
  error?: string;
  details?: string;
}

export async function POST(request: NextRequest) {
  console.log('🚀 开始网络测速...');
  
  try {
    const body = await request.json();
    const { server_id, test_type = 'full' } = body;
    
    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/speed-test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        server_id,
        test_type
      }),
      // 增加超时时间，因为测速可能需要较长时间
      signal: AbortSignal.timeout(120000) // 2分钟超时
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result: SpeedTestResult = await response.json();
    
    if (result.success) {
      console.log('✅ 网络测速完成:', {
        download: result.data?.download_speed,
        upload: result.data?.upload_speed,
        ping: result.data?.ping
      });
    } else {
      console.log('❌ 网络测速失败:', result.error);
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ 网络测速API错误:', error);
    
    return NextResponse.json({
      success: false,
      error: '网络测速失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// GET 方法用于获取可用的测速服务器列表
export async function GET() {
  console.log('📡 获取测速服务器列表...');
  
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/speed-test/servers`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log('✅ 获取测速服务器列表成功');
    
    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ 获取测速服务器列表失败:', error);
    
    return NextResponse.json({
      success: false,
      error: '获取测速服务器列表失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
