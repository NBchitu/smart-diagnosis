import { NextRequest, NextResponse } from 'next/server';

interface SSLCertificate {
  subject: string;
  issuer: string;
  serial_number: string;
  not_before: string;
  not_after: string;
  signature_algorithm: string;
  public_key_algorithm: string;
  key_size: number;
  fingerprint_sha1: string;
  fingerprint_sha256: string;
  san_domains?: string[];
}

interface SSLCheckResult {
  success: boolean;
  data?: {
    hostname: string;
    ip_address: string;
    port: number;
    ssl_version: string;
    cipher_suite: string;
    certificate: SSLCertificate;
    certificate_chain: SSLCertificate[];
    security_analysis: {
      is_valid: boolean;
      is_expired: boolean;
      days_until_expiry: number;
      is_self_signed: boolean;
      has_weak_signature: boolean;
      supports_sni: boolean;
      vulnerabilities: string[];
      security_grade: string; // A+, A, B, C, D, F
    };
    connection_info: {
      handshake_time: number;
      connect_time: number;
      total_time: number;
    };
    timestamp: string;
  };
  error?: string;
  details?: string;
}

export async function POST(request: NextRequest) {
  console.log('🔒 开始SSL检查...');
  
  try {
    const body = await request.json();
    const { hostname, port = 443, check_chain = true } = body;
    
    if (!hostname) {
      return NextResponse.json({
        success: false,
        error: '请提供要检查的主机名'
      }, { status: 400 });
    }

    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/ssl-check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        hostname,
        port,
        check_chain
      }),
      signal: AbortSignal.timeout(30000) // 30秒超时
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result: SSLCheckResult = await response.json();
    
    if (result.success) {
      console.log('✅ SSL检查完成:', {
        hostname: result.data?.hostname,
        ssl_version: result.data?.ssl_version,
        security_grade: result.data?.security_analysis.security_grade,
        days_until_expiry: result.data?.security_analysis.days_until_expiry
      });
    } else {
      console.log('❌ SSL检查失败:', result.error);
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ SSL检查API错误:', error);
    
    return NextResponse.json({
      success: false,
      error: 'SSL检查失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
