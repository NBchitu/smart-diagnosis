import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const taskId = searchParams.get('task_id');

    if (!taskId) {
      return NextResponse.json({
        success: false,
        error: '缺少task_id参数'
      }, { status: 400 });
    }

    // 调用后端API获取原始数据包文件
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/capture/download?task_id=${taskId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/octet-stream',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: '下载失败' }));
      return NextResponse.json({
        success: false,
        error: errorData.error || '下载失败'
      }, { status: response.status });
    }

    // 获取文件内容
    const fileBuffer = await response.arrayBuffer();
    
    // 设置响应头
    const headers = new Headers();
    headers.set('Content-Type', 'application/octet-stream');
    headers.set('Content-Disposition', `attachment; filename="capture_${taskId}.pcap"`);
    headers.set('Content-Length', fileBuffer.byteLength.toString());

    return new NextResponse(fileBuffer, {
      status: 200,
      headers
    });

  } catch (error) {
    console.error('下载原始数据包失败:', error);
    return NextResponse.json({
      success: false,
      error: '下载失败，请稍后重试'
    }, { status: 500 });
  }
}
