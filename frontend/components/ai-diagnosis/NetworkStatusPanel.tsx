'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Wifi, 
  Activity, 
  Globe,
  SignalIcon,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface NetworkStatus {
  isConnected: boolean;
  signalStrength: number;
  downloadSpeed: number;
  uploadSpeed: number;
  latency: number;
  connectedNetwork: string;
  ipAddress: string;
}

export function NetworkStatusPanel() {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isConnected: true,
    signalStrength: 85,
    downloadSpeed: 45.2,
    uploadSpeed: 12.8,
    latency: 23,
    connectedNetwork: 'WiFi-Home-5G',
    ipAddress: '192.168.1.100'
  });



  // 模拟网络状态更新
  useEffect(() => {
    const interval = setInterval(() => {
      // 模拟网络状态变化
      setNetworkStatus(prev => ({
        ...prev,
        signalStrength: Math.max(30, Math.min(100, prev.signalStrength + (Math.random() - 0.5) * 10)),
        latency: Math.max(5, Math.min(100, prev.latency + (Math.random() - 0.5) * 5))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getSignalIcon = (strength: number) => {
    if (strength >= 70) return <SignalIcon className="h-4 w-4 text-green-600" />;
    if (strength >= 40) return <SignalIcon className="h-4 w-4 text-yellow-600" />;
    return <SignalIcon className="h-4 w-4 text-red-600" />;
  };

  const getConnectionStatus = () => {
    if (networkStatus.isConnected) {
      return (
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
          <CheckCircle className="h-3 w-3 mr-1" />
          已连接
        </Badge>
      );
    }
    return (
      <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
        <XCircle className="h-3 w-3 mr-1" />
        未连接
      </Badge>
    );
  };

  const getLatencyStatus = (latency: number) => {
    if (latency <= 30) {
      return <span className="text-green-600">优秀</span>;
    } else if (latency <= 60) {
      return <span className="text-yellow-600">良好</span>;
    } else {
      return <span className="text-red-600">较差</span>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center justify-between">
          <span className="flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            网络状态
          </span>
          {getConnectionStatus()}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 当前连接信息 */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">当前网络</span>
            <span className="text-sm font-medium flex items-center">
              <Wifi className="h-3 w-3 mr-1" />
              {networkStatus.connectedNetwork}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">IP地址</span>
            <span className="text-sm font-medium">{networkStatus.ipAddress}</span>
          </div>
        </div>

        {/* 信号强度 */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">信号强度</span>
            <div className="flex items-center space-x-2">
              {getSignalIcon(networkStatus.signalStrength)}
              <span className="text-sm font-medium">{networkStatus.signalStrength}%</span>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                networkStatus.signalStrength >= 70 ? 'bg-green-500' :
                networkStatus.signalStrength >= 40 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${networkStatus.signalStrength}%` }}
            />
          </div>
        </div>

        {/* 网络性能 */}
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700">网络性能</div>
          
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">下载速度</span>
              <span className="font-medium">{networkStatus.downloadSpeed} Mbps</span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">上传速度</span>
              <span className="font-medium">{networkStatus.uploadSpeed} Mbps</span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">延迟</span>
              <span className="font-medium">
                {networkStatus.latency}ms {getLatencyStatus(networkStatus.latency)}
              </span>
            </div>
          </div>
        </div>

        {/* 快速状态提示 */}
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <Activity className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-gray-600">
              {networkStatus.signalStrength >= 70 && networkStatus.latency <= 30 && (
                <span className="text-green-600 font-medium">网络状态良好，可以正常使用</span>
              )}
              {(networkStatus.signalStrength < 70 || networkStatus.latency > 30) && (
                <span className="text-yellow-600 font-medium">网络性能一般，建议进行诊断</span>
              )}
              {networkStatus.signalStrength < 40 && networkStatus.latency > 60 && (
                <span className="text-red-600 font-medium">网络状态较差，需要紧急处理</span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 