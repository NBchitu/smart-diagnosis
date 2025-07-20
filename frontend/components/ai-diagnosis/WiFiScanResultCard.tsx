'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Wifi, 
  Signal, 
  Router,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  BarChart3,
  Network,
  Smartphone
} from 'lucide-react';
import { cn } from '@/lib/utils';
import ChannelInterferenceChart from '../wifi/ChannelInterferenceChart';

interface WiFiNetwork {
  ssid: string;
  bssid: string;
  signal: number;
  quality: number;
  channel: number;
  frequency: number;
  encryption: string;
  timestamp: number;
}

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

interface ChannelAnalysis {
  "2.4ghz": Record<number, {
    level: number;
    count: number;
    avg_signal: number;
    networks: Array<{ssid: string; signal: number}>;
  }>;
  "5ghz": Record<number, {
    level: number;
    count: number;
    avg_signal: number;
    networks: Array<{ssid: string; signal: number}>;
  }>;
  summary: {
    total_24ghz_networks: number;
    total_5ghz_networks: number;
    most_crowded_24ghz: number;
    least_crowded_24ghz: number;
  };
}

interface Recommendations {
  need_adjustment: boolean;
  current_channel: number | null;
  current_band: string | null;
  recommended_channels: Array<{
    channel: number;
    interference_level: number;
    network_count: number;
    improvement: number;
  }>;
  reasons: string[];
}

interface WiFiScanData {
  current_wifi: CurrentWiFi | null;
  networks: WiFiNetwork[];
  channel_analysis: ChannelAnalysis;
  recommendations: Recommendations;
  scan_time: number;
  total_networks: number;
  type: string;
  timestamp: string;
}

interface WiFiScanResultCardProps {
  result: WiFiScanData;
  className?: string;
}

export function WiFiScanResultCard({ result, className }: WiFiScanResultCardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'recommendations'>('overview');
  const [showDetails, setShowDetails] = useState(false);

  // 获取信号强度图标和样式
  const getSignalInfo = (strength: number) => {
    if (strength >= -30) return {
      icon: <Signal className="w-4 h-4 text-green-500" />,
      text: '优秀',
      color: 'text-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    };
    if (strength >= -50) return {
      icon: <Signal className="w-4 h-4 text-green-400" />,
      text: '良好', 
      color: 'text-green-400',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    };
    if (strength >= -70) return {
      icon: <Signal className="w-4 h-4 text-yellow-500" />,
      text: '一般',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200'
    };
    return {
      icon: <Signal className="w-4 h-4 text-red-500" />,
      text: '较差',
      color: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200'
    };
  };

  // 获取整体WiFi状态
  const getOverallStatus = () => {
    if (!result.current_wifi?.connected) {
      return {
        icon: <AlertTriangle className="w-5 h-5 text-red-500" />,
        text: '未连接WiFi',
        color: 'bg-red-50 border-red-200',
        textColor: 'text-red-700'
      };
    }

    const signalStrength = result.current_wifi.signal_strength;
    const needsAdjustment = result.recommendations?.need_adjustment;

    if (signalStrength >= -50 && !needsAdjustment) {
      return {
        icon: <CheckCircle className="w-5 h-5 text-green-500" />,
        text: 'WiFi状态优秀',
        color: 'bg-green-50 border-green-200',
        textColor: 'text-green-700'
      };
    } else if (signalStrength >= -70 && !needsAdjustment) {
      return {
        icon: <CheckCircle className="w-5 h-5 text-blue-500" />,
        text: 'WiFi状态良好',
        color: 'bg-blue-50 border-blue-200',
        textColor: 'text-blue-700'
      };
    } else {
      return {
        icon: <AlertTriangle className="w-5 h-5 text-yellow-500" />,
        text: 'WiFi需要优化',
        color: 'bg-yellow-50 border-yellow-200',
        textColor: 'text-yellow-700'
      };
    }
  };

  // 获取频段分布
  const getBandDistribution = () => {
    const ghz24Count = result.channel_analysis?.summary?.total_24ghz_networks || 0;
    const ghz5Count = result.channel_analysis?.summary?.total_5ghz_networks || 0;
    const total = ghz24Count + ghz5Count;
    
    return {
      ghz24: { count: ghz24Count, percentage: total > 0 ? (ghz24Count / total * 100) : 0 },
      ghz5: { count: ghz5Count, percentage: total > 0 ? (ghz5Count / total * 100) : 0 },
      total
    };
  };

  const overallStatus = getOverallStatus();
  const bandDistribution = getBandDistribution();
  const currentSignal = result.current_wifi ? getSignalInfo(result.current_wifi.signal_strength) : null;

  return (
    <Card className={cn("w-full", className, overallStatus.color)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {overallStatus.icon}
            <div>
              <CardTitle className="text-lg font-semibold text-gray-900">
                WiFi扫描分析结果
              </CardTitle>
              <p className={cn("text-sm mt-1", overallStatus.textColor)}>
                发现 {result.total_networks} 个网络
              </p>
            </div>
          </div>
          <Badge 
            variant="outline"
            className={cn("text-xs", overallStatus.textColor)}
          >
            {overallStatus.text}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 当前WiFi状态 - 如果已连接 */}
        {result.current_wifi?.connected && currentSignal && (
          <div className={cn("rounded-lg p-3 border", currentSignal.bgColor, currentSignal.borderColor)}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Wifi className="w-4 h-4 text-blue-600" />
                <span className="font-medium text-gray-900">当前连接</span>
              </div>
              <Badge variant="outline" className={currentSignal.color}>
                {currentSignal.text}
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-600">网络：</span>
                <span className="font-medium ml-1">{result.current_wifi.ssid}</span>
              </div>
              <div>
                <span className="text-gray-600">信号：</span>
                <span className={cn("font-medium ml-1", currentSignal.color)}>
                  {result.current_wifi.signal_strength} dBm
                </span>
              </div>
              <div>
                <span className="text-gray-600">信道：</span>
                <span className="font-medium ml-1">{result.current_wifi.channel}</span>
              </div>
              <div>
                <span className="text-gray-600">频段：</span>
                <span className="font-medium ml-1">
                  {result.current_wifi.frequency >= 5000 ? '5GHz' : '2.4GHz'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* 网络统计概览 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Network className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">2.4GHz网络</span>
            </div>
            <div className="text-2xl font-bold text-blue-900">
              {bandDistribution.ghz24.count}
            </div>
            <div className="text-xs text-blue-600">
              占比 {bandDistribution.ghz24.percentage.toFixed(1)}%
            </div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <Router className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-800">5GHz网络</span>
            </div>
            <div className="text-2xl font-bold text-purple-900">
              {bandDistribution.ghz5.count}
            </div>
            <div className="text-xs text-purple-600">
              占比 {bandDistribution.ghz5.percentage.toFixed(1)}%
            </div>
          </div>
        </div>

        {/* 标签页导航 */}
        <div className="flex border-b border-gray-200 -mx-1">
          <button
            onClick={() => setActiveTab('overview')}
            className={cn(
              "px-3 py-2 text-sm font-medium border-b-2 transition-colors",
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            )}
          >
            网络列表
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={cn(
              "px-3 py-2 text-sm font-medium border-b-2 transition-colors",
              activeTab === 'analysis'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            )}
          >
            信道分析
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={cn(
              "px-3 py-2 text-sm font-medium border-b-2 transition-colors",
              activeTab === 'recommendations'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            )}
          >
            优化建议
          </button>
        </div>

        {/* 标签页内容 */}
        <div className="mt-4">
          {/* 网络列表 */}
          {activeTab === 'overview' && (
            <div className="space-y-2">
              {result.networks?.slice(0, showDetails ? undefined : 5).map((network, index) => {
                const signalInfo = getSignalInfo(network.signal);
                return (
                  <div key={`${network.bssid}-${index}`} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      {signalInfo.icon}
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm truncate">{network.ssid || '隐藏网络'}</div>
                        <div className="text-xs text-gray-500">
                          信道 {network.channel} • {network.encryption}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={cn("text-sm font-medium", signalInfo.color)}>
                        {network.signal} dBm
                      </div>
                      <div className="text-xs text-gray-500">
                        {signalInfo.text}
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {result.networks && result.networks.length > 5 && (
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="w-full py-2 text-sm text-blue-600 hover:text-blue-800 flex items-center justify-center gap-1"
                >
                  {showDetails ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      收起
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      显示全部 {result.networks.length} 个网络
                    </>
                  )}
                </button>
              )}
            </div>
          )}

          {/* 信道分析 */}
          {activeTab === 'analysis' && (
            <div>
              {result.channel_analysis && (
                <ChannelInterferenceChart channelData={result.channel_analysis} />
              )}
            </div>
          )}

          {/* 优化建议 */}
          {activeTab === 'recommendations' && (
            <div className="space-y-3">
              {result.recommendations?.need_adjustment ? (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-600" />
                    <span className="font-medium text-yellow-800">建议优化</span>
                  </div>
                  <div className="space-y-2">
                    {result.recommendations.reasons?.map((reason, index) => (
                      <div key={index} className="text-sm text-yellow-700">
                        • {reason}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="font-medium text-green-800">当前配置良好</span>
                  </div>
                  <div className="text-sm text-green-700">
                    您的WiFi设置已经优化，无需调整。
                  </div>
                </div>
              )}

              {result.recommendations?.recommended_channels && result.recommendations.recommended_channels.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">推荐信道：</h4>
                  <div className="space-y-2">
                    {result.recommendations.recommended_channels.slice(0, 3).map((channel, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-blue-50 rounded-lg">
                        <div>
                          <span className="font-medium text-blue-900">信道 {channel.channel}</span>
                          <div className="text-xs text-blue-600">
                            {channel.network_count} 个网络使用
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-green-600">
                            +{channel.improvement}% 改善
                          </div>
                          <div className="text-xs text-gray-500">
                            干扰等级: {channel.interference_level}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 扫描时间 */}
        <div className="flex items-center gap-2 text-xs text-gray-500 pt-2 border-t border-gray-200">
          <Clock className="w-3 h-3" />
          <span>扫描时间: {new Date(result.timestamp).toLocaleString()}</span>
        </div>
      </CardContent>
    </Card>
  );
} 