'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Wifi, 
  Signal, 
  Radio,
  Shield,
  Clock,
  Router
} from 'lucide-react';

interface CurrentWiFi {
  ssid: string;
  signal_strength: number;
  signal_quality: number;
  channel: number;
  frequency: number;
  interface: string;
  encryption: string;
  connected: boolean;
  timestamp: number;
}

interface CurrentWiFiCardProps {
  wifi: CurrentWiFi;
}

const CurrentWiFiCard: React.FC<CurrentWiFiCardProps> = ({ wifi }) => {
  // 获取信号强度等级
  const getSignalLevel = (strength: number) => {
    if (strength >= -30) return { level: 'excellent', text: '优秀', color: 'text-green-500' };
    if (strength >= -50) return { level: 'good', text: '良好', color: 'text-green-400' };
    if (strength >= -70) return { level: 'fair', text: '一般', color: 'text-yellow-500' };
    return { level: 'poor', text: '较差', color: 'text-red-500' };
  };

  // 获取频段信息
  const getBandInfo = (frequency: number) => {
    if (frequency < 3000) {
      return { band: '2.4GHz', color: 'bg-blue-100 text-blue-700' };
    } else {
      return { band: '5GHz', color: 'bg-purple-100 text-purple-700' };
    }
  };

  // 获取加密类型颜色
  const getEncryptionColor = (encryption: string) => {
    if (encryption.includes('WPA3')) return 'bg-green-100 text-green-700';
    if (encryption.includes('WPA2')) return 'bg-blue-100 text-blue-700';
    if (encryption.includes('WPA')) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  // 获取信号强度进度条宽度
  const getSignalProgress = (quality: number) => {
    return Math.max(10, Math.min(100, quality));
  };

  // 格式化时间
  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const signalInfo = getSignalLevel(wifi.signal_strength);
  const bandInfo = getBandInfo(wifi.frequency);

  return (
    <Card className="border-green-200 bg-green-50/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-base sm:text-lg flex items-center gap-2">
          <div className="relative">
            <Wifi className="w-5 h-5 text-green-600" />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
          当前连接的网络
          <Badge className="bg-green-100 text-green-700 text-xs">已连接</Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 网络名称 */}
        <div className="flex items-center gap-3">
          <Router className="w-5 h-5 text-gray-500" />
          <div>
            <div className="font-medium text-lg">{wifi.ssid}</div>
            <div className="text-sm text-gray-600">网络接口: {wifi.interface}</div>
          </div>
        </div>

        {/* 信号强度 */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Signal className={`w-4 h-4 ${signalInfo.color}`} />
              <span className="text-sm font-medium">信号强度</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-medium ${signalInfo.color}`}>
                {signalInfo.text}
              </span>
              <span className="text-sm text-gray-600">
                {wifi.signal_strength} dBm
              </span>
            </div>
          </div>
          
          {/* 信号强度进度条 */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                signalInfo.level === 'excellent' ? 'bg-green-500' :
                signalInfo.level === 'good' ? 'bg-green-400' :
                signalInfo.level === 'fair' ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${getSignalProgress(wifi.signal_quality)}%` }}
            ></div>
          </div>
          
          <div className="text-xs text-gray-500">
            信号质量: {wifi.signal_quality}%
          </div>
        </div>

        {/* 网络参数 */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
          {/* 频段 */}
          <div className="text-center p-2 sm:p-3 bg-white rounded-lg border">
            <Radio className="w-4 h-4 sm:w-5 sm:h-5 mx-auto mb-1 text-blue-500" />
            <div className="text-xs sm:text-sm text-gray-600">频段</div>
            <Badge className={`text-xs mt-1 ${bandInfo.color}`}>
              {bandInfo.band}
            </Badge>
          </div>

          {/* 信道 */}
          <div className="text-center p-2 sm:p-3 bg-white rounded-lg border">
            <div className="text-lg sm:text-xl font-bold text-blue-600 mb-1">
              {wifi.channel}
            </div>
            <div className="text-xs sm:text-sm text-gray-600">信道</div>
          </div>

          {/* 频率 */}
          <div className="text-center p-2 sm:p-3 bg-white rounded-lg border">
            <div className="text-sm sm:text-base font-medium text-purple-600 mb-1">
              {wifi.frequency}
            </div>
            <div className="text-xs sm:text-sm text-gray-600">MHz</div>
          </div>

          {/* 加密 */}
          <div className="text-center p-2 sm:p-3 bg-white rounded-lg border">
            <Shield className="w-4 h-4 sm:w-5 sm:h-5 mx-auto mb-1 text-green-500" />
            <div className="text-xs sm:text-sm text-gray-600">加密</div>
            <Badge className={`text-xs mt-1 ${getEncryptionColor(wifi.encryption)}`}>
              {wifi.encryption}
            </Badge>
          </div>
        </div>

        {/* 详细信息 */}
        <div className="pt-3 border-t border-gray-200">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">更新时间:</span>
              <span className="font-medium">{formatTime(wifi.timestamp)}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 flex items-center justify-center">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
              <span className="text-gray-600">连接状态:</span>
              <span className="font-medium text-green-600">
                {wifi.connected ? '已连接' : '未连接'}
              </span>
            </div>
          </div>
        </div>

        {/* 信号质量提示 */}
        <div className="p-3 bg-blue-50 rounded-lg">
          <div className="text-sm">
            <div className="font-medium text-blue-800 mb-1">信号分析</div>
            <div className="text-blue-700 text-xs sm:text-sm">
              {signalInfo.level === 'excellent' && 
                '信号优秀，网络性能最佳，适合所有应用场景。'}
              {signalInfo.level === 'good' && 
                '信号良好，网络性能稳定，适合大部分应用场景。'}
              {signalInfo.level === 'fair' && 
                '信号一般，可能会影响网络速度，建议靠近路由器。'}
              {signalInfo.level === 'poor' && 
                '信号较差，网络可能不稳定，建议检查网络环境或更换位置。'}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CurrentWiFiCard; 