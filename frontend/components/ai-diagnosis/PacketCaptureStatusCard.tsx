'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  CheckCircle,
  Pause,
  Clock,
  Database,
  Monitor,
  FileText,
  Download
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PacketCaptureStoppedData {
  session_id: string;
  message: string;
  final_packet_count: number;
  total_duration: number;
  status: string;
  saved_files?: string[]; // 保存的文件列表
}

interface PacketCaptureStatusData {
  session_id: string;
  is_capturing: boolean;
  current_packet_count: number;
  elapsed_time: number;
  remaining_time?: number;
  status: string;
  saved_files?: string[]; // 保存的文件列表
}

interface PacketCaptureStartedData {
  session_id: string;
  target: string;
  mode: string;
  duration: number;
  interface: string;
  status: string;
  message: string;
  start_time: string;
}

interface PacketCaptureStatusCardProps {
  type: 'packet_capture_stopped' | 'packet_capture_status' | 'packet_capture_started';
  data: PacketCaptureStoppedData | PacketCaptureStatusData | PacketCaptureStartedData;
  className?: string;
}

export function PacketCaptureStatusCard({ type, data, className }: PacketCaptureStatusCardProps) {
  
  // 获取状态信息
  const getStatusInfo = () => {
    if (type === 'packet_capture_stopped') {
      return {
        icon: <Pause className="w-5 h-5 text-yellow-500" />,
        title: '抓包已停止',
        text: '任务完成',
        color: 'bg-yellow-50 border-yellow-200'
      };
    }
    
    if (type === 'packet_capture_started') {
      return {
        icon: <Activity className="w-5 h-5 text-green-500 animate-pulse" />,
        title: '抓包已启动',
        text: '正在启动',
        color: 'bg-green-50 border-green-200'
      };
    }
    
    const statusData = data as PacketCaptureStatusData;
    if (statusData.is_capturing) {
      return {
        icon: <Activity className="w-5 h-5 text-blue-500 animate-pulse" />,
        title: '抓包状态',
        text: '正在进行',
        color: 'bg-blue-50 border-blue-200'
      };
    } else {
      return {
        icon: <Monitor className="w-5 h-5 text-gray-500" />,
        title: '抓包状态',
        text: '空闲中',
        color: 'bg-gray-50 border-gray-200'
      };
    }
  };

  const statusInfo = getStatusInfo();

  if (type === 'packet_capture_stopped') {
    const stoppedData = data as PacketCaptureStoppedData;
    
    return (
      <Card className={cn("w-full", className, statusInfo.color)}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              {statusInfo.icon}
              <div>
                <CardTitle className="text-lg font-semibold text-gray-900">
                  {statusInfo.title}
                </CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  {stoppedData.message}
                </p>
              </div>
            </div>
            <Badge variant="secondary" className="text-xs">
              {statusInfo.text}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* 停止抓包的统计信息 */}
          <div className="grid grid-cols-2 gap-4">
            {/* 总数据包 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">总数据包</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-gray-900">
                  {stoppedData.final_packet_count.toLocaleString()}
                </span>
                <span className="text-sm text-gray-500">个</span>
              </div>
            </div>

            {/* 总时长 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">总时长</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-gray-900">
                  {stoppedData.total_duration}
                </span>
                <span className="text-sm text-gray-500">秒</span>
              </div>
            </div>
          </div>

          {/* 会话信息 */}
          <div className="text-xs text-gray-500">
            会话ID: {stoppedData.session_id}
          </div>

          {/* 完成提示 */}
          <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">抓包任务已成功停止</span>
            </div>
            <p className="text-green-700 mt-1">
              数据包分析已完成，可查看详细结果。
            </p>
          </div>

          {/* 保存文件信息 */}
          {stoppedData.saved_files && stoppedData.saved_files.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
              <div className="flex items-center gap-2 text-blue-600 mb-2">
                <FileText className="w-4 h-4" />
                <span className="font-medium">数据已保存到本地</span>
              </div>
              <div className="space-y-1">
                {stoppedData.saved_files.map((filePath, index) => {
                  const fileName = filePath.split('/').pop() || filePath;
                  const fileType = fileName.includes('detailed') ? 'JSON详细数据' : 
                                 fileName.includes('summary') ? '可读摘要' : 
                                 fileName.includes('raw') ? '原始数据' : '数据文件';
                  
                  return (
                    <div key={index} className="flex items-center gap-2 text-blue-700">
                      <Download className="w-3 h-3" />
                      <span className="text-xs font-mono bg-blue-100 px-1 rounded">
                        {fileName}
                      </span>
                      <span className="text-xs text-blue-600">({fileType})</span>
                    </div>
                  );
                })}
              </div>
              <p className="text-blue-700 mt-2 text-xs">
                文件保存在服务器的 backend/data/packet_captures/ 目录中
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // 处理抓包启动类型
  if (type === 'packet_capture_started') {
    const startedData = data as PacketCaptureStartedData;
    
    return (
      <Card className={cn("w-full", className, statusInfo.color)}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              {statusInfo.icon}
              <div>
                <CardTitle className="text-lg font-semibold text-gray-900">
                  {statusInfo.title}
                </CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  {startedData.message}
                </p>
              </div>
            </div>
            <Badge variant="default" className="text-xs bg-green-500">
              {statusInfo.text}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* 启动配置信息 */}
          <div className="grid grid-cols-2 gap-4">
            {/* 抓包目标 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Monitor className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">抓包目标</span>
              </div>
              <div className="text-lg font-bold text-gray-900 break-all">
                {startedData.target}
              </div>
            </div>

            {/* 预计时长 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">预计时长</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-gray-900">
                  {startedData.duration}
                </span>
                <span className="text-sm text-gray-500">秒</span>
              </div>
            </div>
          </div>

          {/* 配置详情 */}
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">抓包模式:</span>
              <span className="font-medium">{startedData.mode}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">网络接口:</span>
              <span className="font-medium">{startedData.interface}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">开始时间:</span>
              <span className="font-medium">{new Date(startedData.start_time).toLocaleTimeString()}</span>
            </div>
          </div>

          {/* 会话信息 */}
          <div className="text-xs text-gray-500">
            会话ID: {startedData.session_id}
          </div>

          {/* 启动提示 */}
          <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
            <div className="flex items-center gap-2 text-green-600">
              <Activity className="w-4 h-4 animate-pulse" />
              <span className="font-medium">抓包任务已启动</span>
            </div>
            <p className="text-green-700 mt-1">
              正在捕获网络数据包，系统将自动监控抓包状态并在完成后进行分析。
            </p>
          </div>

          {/* 自动监控提示 */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
            <div className="flex items-center gap-2 text-blue-600">
              <Clock className="w-4 h-4" />
              <span className="font-medium">自动状态监控</span>
            </div>
            <p className="text-blue-700 mt-1">
              系统将每5秒检查一次抓包状态，无需手动刷新。抓包完成后将自动显示分析结果。
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 状态查询显示
  const statusData = data as PacketCaptureStatusData;
  const progressPercentage = statusData.remaining_time 
    ? ((statusData.elapsed_time / (statusData.elapsed_time + statusData.remaining_time)) * 100)
    : 0;

  return (
    <Card className={cn("w-full", className, statusInfo.color)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {statusInfo.icon}
            <div>
              <CardTitle className="text-lg font-semibold text-gray-900">
                {statusInfo.title}
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                会话ID: {statusData.session_id}
              </p>
            </div>
          </div>
          <Badge 
            variant={statusData.is_capturing ? 'default' : 'secondary'} 
            className="text-xs"
          >
            {statusInfo.text}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {statusData.is_capturing ? (
          <>
            {/* 进行中的抓包统计 */}
            <div className="grid grid-cols-2 gap-4">
              {/* 当前数据包 */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">当前数据包</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-gray-900">
                    {statusData.current_packet_count.toLocaleString()}
                  </span>
                  <span className="text-sm text-gray-500">个</span>
                </div>
              </div>

              {/* 已用时间 */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">已用时间</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-gray-900">
                    {statusData.elapsed_time}
                  </span>
                  <span className="text-sm text-gray-500">秒</span>
                </div>
              </div>
            </div>

            {/* 进度条 */}
            {statusData.remaining_time !== undefined && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">抓包进度</span>
                  <span className="text-gray-500">
                    剩余 {statusData.remaining_time} 秒
                  </span>
                </div>
                <Progress value={progressPercentage} className="h-2" />
              </div>
            )}

            {/* 进行中提示 */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
              <div className="flex items-center gap-2 text-blue-600">
                <Activity className="w-4 h-4 animate-pulse" />
                <span className="font-medium">抓包正在进行中</span>
              </div>
              <p className="text-blue-700 mt-1">
                系统正在捕获和分析网络数据包，请稍候...
              </p>
            </div>
          </>
        ) : (
          <>
            {/* 已完成状态显示 */}
            {statusData.current_packet_count > 0 ? (
              <div className="space-y-4">
                {/* 完成状态的统计信息 */}
                <div className="grid grid-cols-2 gap-4">
                  {/* 总数据包 */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">总数据包</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-gray-900">
                        {statusData.current_packet_count.toLocaleString()}
                      </span>
                      <span className="text-sm text-gray-500">个</span>
                    </div>
                  </div>

                  {/* 总时长 */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">总时长</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-gray-900">
                        {statusData.elapsed_time}
                      </span>
                      <span className="text-sm text-gray-500">秒</span>
                    </div>
                  </div>
                </div>

                {/* 完成提示 */}
                <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="w-4 h-4" />
                    <span className="font-medium">抓包任务已完成</span>
                  </div>
                  <p className="text-green-700 mt-1">
                    数据包分析已完成，数据已自动保存。
                  </p>
                </div>

                {/* 保存文件信息 */}
                {statusData.saved_files && statusData.saved_files.length > 0 && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
                    <div className="flex items-center gap-2 text-blue-600 mb-2">
                      <FileText className="w-4 h-4" />
                      <span className="font-medium">数据已保存到本地</span>
                    </div>
                    <div className="space-y-1">
                      {statusData.saved_files.map((filePath, index) => {
                        const fileName = filePath.split('/').pop() || filePath;
                        const fileType = fileName.includes('detailed') ? 'JSON详细数据' : 
                                       fileName.includes('summary') ? '可读摘要' : 
                                       fileName.includes('raw') ? '原始数据' : '数据文件';
                        
                        return (
                          <div key={index} className="flex items-center gap-2 text-blue-700">
                            <Download className="w-3 h-3" />
                            <span className="text-xs font-mono bg-blue-100 px-1 rounded">
                              {fileName}
                            </span>
                            <span className="text-xs text-blue-600">({fileType})</span>
                          </div>
                        );
                      })}
                    </div>
                    <p className="text-blue-700 mt-2 text-xs">
                      文件保存在服务器的 backend/data/packet_captures/ 目录中
                    </p>
                  </div>
                )}
              </div>
            ) : (
              /* 空闲状态 */
              <div className="text-center py-8">
                <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  当前没有进行抓包任务
                </h3>
                <p className="text-sm text-gray-500">
                  系统处于空闲状态，可以开始新的网络分析任务
                </p>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
} 