import { NextRequest, NextResponse } from 'next/server';

interface DNSServer {
  name: string;
  ip: string;
  location: string;
}

interface DNSTestResult {
  server: DNSServer;
  domain: string;
  query_type: string;
  response_time: number;
  status: 'success' | 'timeout' | 'error';
  resolved_ips?: string[];
  error_message?: string;
}

interface DNSTestResponse {
  success: boolean;
  data?: {
    domain: string;
    test_results: DNSTestResult[];
    summary: {
      fastest_server: DNSServer;
      slowest_server: DNSServer;
      avg_response_time: number;
      success_rate: number;
      total_tests: number;
    };
    timestamp: string;
  };
  error?: string;
  details?: string;
}

export async function POST(request: NextRequest) {
  console.log('🔍 开始DNS测试...');
  
  try {
    const body = await request.json();
    const { domain, query_type = 'A', custom_servers = [] } = body;
    
    if (!domain) {
      return NextResponse.json({
        success: false,
        error: '请提供要测试的域名'
      }, { status: 400 });
    }

    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/dns-test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        domain,
        query_type,
        custom_servers
      }),
      signal: AbortSignal.timeout(30000) // 30秒超时
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result: DNSTestResponse = await response.json();
    
    if (result.success) {
      console.log('✅ DNS测试完成:', {
        domain: result.data?.domain,
        total_tests: result.data?.summary.total_tests,
        success_rate: result.data?.summary.success_rate
      });
    } else {
      console.log('❌ DNS测试失败:', result.error);
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ DNS测试API错误:', error);
    
    return NextResponse.json({
      success: false,
      error: 'DNS测试失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
