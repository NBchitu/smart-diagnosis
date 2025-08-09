import { NextRequest, NextResponse } from 'next/server';

interface QualityMetric {
  timestamp: string;
  ping_latency: number;
  jitter: number;
  packet_loss: number;
  download_speed?: number;
  upload_speed?: number;
}

interface NetworkQualityResult {
  success: boolean;
  data?: {
    target: string;
    test_duration: number;
    interval: number;
    metrics: QualityMetric[];
    summary: {
      avg_latency: number;
      max_latency: number;
      min_latency: number;
      avg_jitter: number;
      total_packet_loss: number;
      stability_score: number; // 0-100
      quality_grade: string; // Excellent, Good, Fair, Poor
    };
    recommendations: string[];
    timestamp: string;
  };
  error?: string;
  details?: string;
}

export async function POST(request: NextRequest) {
  console.log('📊 开始网络质量监控...');
  
  try {
    const body = await request.json();
    const { 
      target = 'google.com',
      duration = 60,
      interval = 5,
      include_speed_test = false
    } = body;

    // 调用后端 API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/network-quality`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        target,
        duration,
        interval,
        include_speed_test
      }),
      // 网络质量监控需要较长时间
      signal: AbortSignal.timeout((duration + 30) * 1000) // 额外30秒缓冲
    });

    if (!response.ok) {
      throw new Error(`后端API调用失败: ${response.status} ${response.statusText}`);
    }

    const result: NetworkQualityResult = await response.json();
    
    if (result.success) {
      console.log('✅ 网络质量监控完成:', {
        target: result.data?.target,
        duration: result.data?.test_duration,
        quality_grade: result.data?.summary.quality_grade,
        stability_score: result.data?.summary.stability_score
      });
    } else {
      console.log('❌ 网络质量监控失败:', result.error);
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ 网络质量监控API错误:', error);
    
    return NextResponse.json({
      success: false,
      error: '网络质量监控失败',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
