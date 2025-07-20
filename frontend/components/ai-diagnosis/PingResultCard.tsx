'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Clock, 
  Target, 
  Activity,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PingResult {
  host: string;
  success: boolean;
  packets_transmitted: number;
  packets_received: number;
  packet_loss: number;
  min_time?: number;
  max_time?: number;
  avg_time?: number;
  times?: number[];
  output?: string;
  error?: string;
  return_code: number;
}

// 后端返回的数据格式接口
interface BackendPingResult {
  host: string;
  packets_sent: number;
  packets_received: number;
  packet_loss: string;
  min_latency?: string;
  avg_latency?: string;
  max_latency?: string;
  status: string;
  timestamp: string;
}

interface PingResultCardProps {
  result: PingResult | BackendPingResult;
  className?: string;
}

// 数据转换适配器函数
function adaptPingResult(result: any): PingResult {
  // 如果已经是正确格式，直接返回
  if (result.packets_transmitted !== undefined && result.avg_time !== undefined) {
    return result as PingResult;
  }

  // 转换字符串延迟值为数字（去掉"ms"后缀）
  const parseLatency = (latency?: string): number | undefined => {
    if (!latency) return undefined;
    const match = latency.match(/^(\d+\.?\d*)ms?$/);
    return match ? parseFloat(match[1]) : undefined;
  };

  // 转换丢包率字符串为数字
  const parsePacketLoss = (loss: string): number => {
    if (!loss) return 0;
    const match = loss.match(/^(\d+\.?\d*)%$/);
    return match ? parseFloat(match[1]) : 0;
  };

  // 转换为标准格式
  const adapted: PingResult = {
    host: result.host || 'unknown',
    success: result.status === 'success',
    packets_transmitted: result.packets_sent || 0,
    packets_received: result.packets_received || 0,
    packet_loss: parsePacketLoss(result.packet_loss || '0%'),
    min_time: parseLatency(result.min_latency),
    max_time: parseLatency(result.max_latency),
    avg_time: parseLatency(result.avg_latency),
    times: [], // 后端没有返回单次测试结果，设为空数组
    output: '', // 后端没有返回原始输出
    error: '', // 后端没有返回错误信息
    return_code: 0 // 后端没有返回返回码
  };

  return adapted;
}

export function PingResultCard({ result, className }: PingResultCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  // 适配数据格式
  const adaptedResult = adaptPingResult(result);

  // 获取连接状态
  const getConnectionStatus = () => {
    if (!adaptedResult.success) {
      return {
        status: 'failed',
        icon: <XCircle className="w-5 h-5 text-red-500" />,
        text: '连接失败',
        color: 'bg-red-50 border-red-200'
      };
    }
    
    if (adaptedResult.packet_loss > 0) {
      return {
        status: 'unstable',
        icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
        text: '连接不稳定',
        color: 'bg-yellow-50 border-yellow-200'
      };
    }
    
    return {
      status: 'success',
      icon: <CheckCircle className="w-5 h-5 text-green-500" />,
      text: '连接正常',
      color: 'bg-green-50 border-green-200'
    };
  };

  // 获取延迟等级
  const getLatencyLevel = (avgTime: number | undefined) => {
    if (!avgTime || avgTime === undefined) return { level: 'unknown', text: '无数据', color: 'bg-gray-500' };
    if (avgTime < 50) return { level: 'excellent', text: '极佳', color: 'bg-green-500' };
    if (avgTime < 100) return { level: 'good', text: '良好', color: 'bg-blue-500' };
    if (avgTime < 200) return { level: 'fair', text: '一般', color: 'bg-yellow-500' };
    if (avgTime < 500) return { level: 'poor', text: '较差', color: 'bg-orange-500' };
    return { level: 'bad', text: '很差', color: 'bg-red-500' };
  };

  const connectionStatus = getConnectionStatus();
  const latencyLevel = getLatencyLevel(adaptedResult.avg_time);

  return (
    <Card className={cn("w-full bg-white/70 backdrop-blur-xl border border-white/20 shadow-lg shadow-black/5 rounded-2xl", className, connectionStatus.color)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <div className="flex-shrink-0">
              {connectionStatus.icon}
            </div>
            <div className="min-w-0 flex-1">
              <CardTitle className="text-base sm:text-lg font-semibold text-gray-900">
                Ping 测试结果
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1 truncate">
                目标: {adaptedResult.host}
              </p>
            </div>
          </div>
          <Badge
            variant={adaptedResult.success ? 'default' : 'destructive'}
            className="text-xs flex-shrink-0 whitespace-nowrap px-2 py-1 rounded-lg"
          >
            {connectionStatus.text}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 主要统计信息 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* 延迟信息 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">平均延迟</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-baseline gap-1">
                <span className="text-xl sm:text-2xl font-bold text-gray-900">
                  {adaptedResult.avg_time ? adaptedResult.avg_time.toFixed(1) : '--'}
                </span>
                <span className="text-sm text-gray-500">ms</span>
              </div>
              <Badge
                variant="outline"
                className={cn("text-xs text-white flex-shrink-0 px-2 py-1 rounded-lg font-medium", latencyLevel.color)}
              >
                {latencyLevel.text}
              </Badge>
            </div>
          </div>

          {/* 成功率 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">成功率</span>
            </div>
            <div className="space-y-2">
              <div className="flex items-baseline gap-2">
                <span className="text-xl sm:text-2xl font-bold text-gray-900">
                  {adaptedResult.packets_transmitted > 0 ?
                    ((adaptedResult.packets_received / adaptedResult.packets_transmitted) * 100).toFixed(0) :
                    '0'}%
                </span>
                <span className="text-sm text-gray-500 whitespace-nowrap">
                  ({adaptedResult.packets_received}/{adaptedResult.packets_transmitted})
                </span>
              </div>
              <Progress
                value={adaptedResult.packets_transmitted > 0 ?
                  ((adaptedResult.packets_received / adaptedResult.packets_transmitted) * 100) :
                  0}
                className="h-2 bg-gray-200"
              />
            </div>
          </div>
        </div>

        {/* 延迟范围 */}
        {adaptedResult.success && adaptedResult.avg_time && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">延迟范围</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="font-medium text-gray-900 text-xs sm:text-sm">
                  {adaptedResult.min_time ? adaptedResult.min_time.toFixed(1) : '--'}ms
                </div>
                <div className="text-gray-500 text-xs">最小</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="font-medium text-gray-900 text-xs sm:text-sm">
                  {adaptedResult.avg_time ? adaptedResult.avg_time.toFixed(1) : '--'}ms
                </div>
                <div className="text-gray-500 text-xs">平均</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="font-medium text-gray-900 text-xs sm:text-sm">
                  {adaptedResult.max_time ? adaptedResult.max_time.toFixed(1) : '--'}ms
                </div>
                <div className="text-gray-500 text-xs">最大</div>
              </div>
            </div>
          </div>
        )}

        {/* 详细信息切换按钮 */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <span>{showDetails ? '收起详细信息' : '查看详细信息'}</span>
          {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {/* 详细信息 */}
        {showDetails && (
          <div className="space-y-3 pt-3 border-t">
            {/* 基本信息 */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">测试详情</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                <div className="flex justify-between py-1">
                  <span className="text-gray-600">发送数据包:</span>
                  <span className="font-medium">{adaptedResult.packets_transmitted}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-600">接收数据包:</span>
                  <span className="font-medium">{adaptedResult.packets_received}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-600">丢包率:</span>
                  <span className="font-medium">{adaptedResult.packet_loss.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-600">状态:</span>
                  <span className={cn("font-medium", adaptedResult.success ? "text-green-600" : "text-red-600")}>
                    {adaptedResult.success ? '成功' : '失败'}
                  </span>
                </div>
              </div>
            </div>

            {/* 诊断建议 */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">网络诊断</h4>
              <div className="text-sm text-gray-600 space-y-1">
                {adaptedResult.success && adaptedResult.avg_time ? (
                  <>
                    {adaptedResult.avg_time < 50 && (
                      <p className="text-green-600">✓ 网络延迟优秀，适合各种网络应用</p>
                    )}
                    {adaptedResult.avg_time >= 50 && adaptedResult.avg_time < 100 && (
                      <p className="text-blue-600">✓ 网络延迟良好，适合大多数应用</p>
                    )}
                    {adaptedResult.avg_time >= 100 && adaptedResult.avg_time < 200 && (
                      <p className="text-yellow-600">⚠ 网络延迟一般，可能影响实时应用</p>
                    )}
                    {adaptedResult.avg_time >= 200 && (
                      <p className="text-orange-600">⚠ 网络延迟较高，建议检查网络连接</p>
                    )}
                    {adaptedResult.packet_loss > 0 && (
                      <p className="text-red-600">✗ 存在丢包，可能网络不稳定</p>
                    )}
                  </>
                ) : (
                  <p className="text-red-600">✗ 无法连接到目标主机，请检查网络连接或目标主机是否响应ping请求</p>
                )}
              </div>
            </div>

            {/* 原始输出 */}
            {adaptedResult.output && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">原始输出</h4>
                <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto text-gray-700">
                  {adaptedResult.output}
                </pre>
              </div>
            )}

            {/* 错误信息 */}
            {adaptedResult.error && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-red-700">错误信息</h4>
                <pre className="text-xs bg-red-50 p-2 rounded text-red-700">
                  {adaptedResult.error}
                </pre>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
} 