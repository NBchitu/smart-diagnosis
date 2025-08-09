import { NextRequest, NextResponse } from 'next/server';

interface PortScanResult {
  port: number;
  status: 'open' | 'closed' | 'filtered' | 'timeout';
  service?: string;
  response_time?: number;
  banner?: string;
}

interface PortScanResponse {
  success: boolean;
  data?: {
    target: string;
    target_ip: string;
    scan_type: string;
    ports_scanned: number[];
    open_ports: PortScanResult[];
    closed_ports: PortScanResult[];
    filtered_ports: PortScanResult[];
    scan_duration: number;
    timestamp: string;
    summary: {
      total_ports: number;
      open_count: number;
      closed_count: number;
      filtered_count: number;
    };
  };
  error?: string;
  details?: string;
}

export async function POST(request: NextRequest) {
  console.log('🔍 开始端口扫描...');
  
  try {
    const body = await request.json();
    let { 
      target,
      ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443],
      scan_type = 'tcp',
      timeout = 3
    } = body;
    if (!target) target = 'www.baidu.com';
    // if (!target) {
    //   return NextResponse.json({
    //     success: false,
    //     error: '请提供目标主机地址'
    //   }, { status: 400 });
    // }

    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/port-scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        target,
        ports,
        scan_type,
        timeout
      }),
      // 端口扫描可能需要较长时间
      signal: AbortSignal.timeout(120000) // 2分钟超时
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result: PortScanResponse = await response.json();
    
    if (result.success) {
      console.log('✅ 端口扫描完成:', {
        target: result.data?.target,
        total_ports: result.data?.summary.total_ports,
        open_ports: result.data?.summary.open_count
      });
    } else {
      console.log('❌ 端口扫描失败:', result.error);
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ 端口扫描API错误:', error);
    
    return NextResponse.json({
      success: false,
      error: '端口扫描失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
