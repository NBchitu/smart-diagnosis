import { NextRequest, NextResponse } from 'next/server';

// 模拟历史记录存储（实际应用中应该使用数据库）
let historyRecords: any[] = [];

export async function GET() {
  try {
    // 返回最近10条记录，按时间倒序
    const recentRecords = historyRecords
      .sort((a, b) => new Date(b.capture_time).getTime() - new Date(a.capture_time).getTime())
      .slice(0, 10);

    return NextResponse.json({
      success: true,
      records: recentRecords
    });
  } catch (error) {
    console.error('获取历史记录失败:', error);
    return NextResponse.json({
      success: false,
      error: '获取历史记录失败'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const record = await request.json();
    
    // 验证必要字段
    if (!record.task_id || !record.capture_time) {
      return NextResponse.json({
        success: false,
        error: '缺少必要字段'
      }, { status: 400 });
    }

    // 检查是否已存在相同task_id的记录
    const existingIndex = historyRecords.findIndex(r => r.task_id === record.task_id);
    
    if (existingIndex >= 0) {
      // 更新现有记录
      historyRecords[existingIndex] = {
        ...historyRecords[existingIndex],
        ...record,
        updated_time: new Date().toISOString()
      };
    } else {
      // 添加新记录
      historyRecords.push({
        ...record,
        created_time: new Date().toISOString()
      });
    }

    // 保持最多10条记录
    if (historyRecords.length > 10) {
      historyRecords = historyRecords
        .sort((a, b) => new Date(b.capture_time).getTime() - new Date(a.capture_time).getTime())
        .slice(0, 10);
    }

    return NextResponse.json({
      success: true,
      message: '历史记录保存成功'
    });
  } catch (error) {
    console.error('保存历史记录失败:', error);
    return NextResponse.json({
      success: false,
      error: '保存历史记录失败'
    }, { status: 500 });
  }
}

export async function DELETE() {
  try {
    historyRecords = [];
    
    return NextResponse.json({
      success: true,
      message: '历史记录清空成功'
    });
  } catch (error) {
    console.error('清空历史记录失败:', error);
    return NextResponse.json({
      success: false,
      error: '清空历史记录失败'
    }, { status: 500 });
  }
}
