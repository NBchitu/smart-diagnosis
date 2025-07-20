'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Wifi, 
  RefreshCw, 
  Signal, 
  AlertTriangle, 
  CheckCircle,
  Router,
  Smartphone
} from 'lucide-react';
import ChannelInterferenceChart from './ChannelInterferenceChart';
import CurrentWiFiCard from './CurrentWiFiCard';
import WiFiNetworkCard from './WiFiNetworkCard';

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
}

const WiFiScanResults: React.FC = () => {
  const [scanData, setScanData] = useState<WiFiScanData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'recommendations'>('overview');

  // 扫描WiFi网络
  const handleScan = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/wifi/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        // 调试：输出接收到的数据
        console.log('WiFiScanResults received data:', result.data);
        console.log('Channel analysis data:', result.data.channel_analysis);
        
        setScanData(result.data);
      } else {
        throw new Error(result.error || '扫描失败');
      }
    } catch (err: any) {
      console.error('WiFi扫描失败:', err);
      setError(err.message || '扫描失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 页面加载时自动扫描
  useEffect(() => {
    handleScan();
  }, []);

  // 获取信号强度图标
  const getSignalIcon = (strength: number) => {
    if (strength >= -30) return <Signal className="w-4 h-4 text-green-500" />;
    if (strength >= -50) return <Signal className="w-4 h-4 text-green-400" />;
    if (strength >= -70) return <Signal className="w-4 h-4 text-yellow-500" />;
    return <Signal className="w-4 h-4 text-red-500" />;
  };

  // 获取信号强度文本
  const getSignalText = (strength: number) => {
    if (strength >= -30) return '优秀';
    if (strength >= -50) return '良好';
    if (strength >= -70) return '一般';
    return '较差';
  };

  // 获取信号强度颜色
  const getSignalColor = (strength: number) => {
    if (strength >= -30) return 'text-green-500';
    if (strength >= -50) return 'text-green-400';
    if (strength >= -70) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-4 sm:space-y-6 p-2 sm:p-4">
      {/* 头部工具栏 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4">
        <div className="flex items-center gap-2">
          <Wifi className="w-5 h-5 sm:w-6 sm:h-6 text-blue-500" />
          <h1 className="text-lg sm:text-xl font-bold">WiFi 扫描分析</h1>
        </div>
        
        <Button
          onClick={handleScan}
          disabled={isLoading}
          size="sm"
          className="w-full sm:w-auto"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          {isLoading ? '扫描中...' : '重新扫描'}
        </Button>
      </div>

      {/* 错误提示 */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm sm:text-base">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 标签页导航 */}
      {scanData && (
        <div className="flex border-b border-gray-200 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-3 sm:px-4 py-2 text-sm sm:text-base font-medium whitespace-nowrap border-b-2 transition-colors ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            网络概览
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-3 sm:px-4 py-2 text-sm sm:text-base font-medium whitespace-nowrap border-b-2 transition-colors ${
              activeTab === 'analysis'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            信道分析
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-3 sm:px-4 py-2 text-sm sm:text-base font-medium whitespace-nowrap border-b-2 transition-colors ${
              activeTab === 'recommendations'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            优化建议
          </button>
        </div>
      )}

      {/* 内容区域 */}
      {scanData && (
        <div className="space-y-4 sm:space-y-6">
          {/* 网络概览 */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              {/* 当前连接的WiFi */}
              {scanData.current_wifi && (
                <CurrentWiFiCard wifi={scanData.current_wifi} />
              )}

              {/* 扫描统计 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base sm:text-lg">扫描统计</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                    <div className="text-center p-2 sm:p-3 bg-blue-50 rounded-lg">
                      <div className="text-lg sm:text-xl font-bold text-blue-600">
                        {scanData.total_networks}
                      </div>
                      <div className="text-xs sm:text-sm text-gray-600">总网络数</div>
                    </div>
                    <div className="text-center p-2 sm:p-3 bg-green-50 rounded-lg">
                      <div className="text-lg sm:text-xl font-bold text-green-600">
                        {scanData.channel_analysis?.summary?.total_24ghz_networks || 0}
                      </div>
                      <div className="text-xs sm:text-sm text-gray-600">2.4GHz</div>
                    </div>
                    <div className="text-center p-2 sm:p-3 bg-purple-50 rounded-lg">
                      <div className="text-lg sm:text-xl font-bold text-purple-600">
                        {scanData.channel_analysis?.summary?.total_5ghz_networks || 0}
                      </div>
                      <div className="text-xs sm:text-sm text-gray-600">5GHz</div>
                    </div>
                    <div className="text-center p-2 sm:p-3 bg-orange-50 rounded-lg">
                      <div className="text-lg sm:text-xl font-bold text-orange-600">
                        {scanData.channel_analysis?.summary?.most_crowded_24ghz || 0}
                      </div>
                      <div className="text-xs sm:text-sm text-gray-600">拥挤信道</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 周边网络列表 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base sm:text-lg">周边网络 ({scanData.networks.length})</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {scanData.networks.length > 0 ? (
                    <div className="space-y-2 sm:space-y-3">
                      {scanData.networks
                        .sort((a, b) => b.signal - a.signal)
                        .map((network, index) => (
                          <WiFiNetworkCard 
                            key={`${network.bssid}-${index}`} 
                            network={network} 
                          />
                        ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 sm:py-8 text-gray-500">
                      <Wifi className="w-8 h-8 sm:w-12 sm:h-12 mx-auto mb-2 opacity-30" />
                      <p className="text-sm sm:text-base">未发现周边网络</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* 信道分析 */}
          {activeTab === 'analysis' && (
            <div className="space-y-4">
              <ChannelInterferenceChart 
                channelData={scanData.channel_analysis}
                currentChannel={scanData.current_wifi?.channel}
              />
            </div>
          )}

          {/* 优化建议 */}
          {activeTab === 'recommendations' && (
            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base sm:text-lg flex items-center gap-2">
                    {scanData.recommendations?.need_adjustment ? (
                      <AlertTriangle className="w-5 h-5 text-yellow-500" />
                    ) : (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                    信道优化建议
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 当前状态 */}
                  {scanData.current_wifi && (
                    <div className="p-3 sm:p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-medium text-sm sm:text-base mb-2">当前状态</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 text-xs sm:text-sm">
                        <div>
                          <span className="text-gray-600">频段: </span>
                          <span className="font-medium">{scanData.recommendations?.current_band || '未知'}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">信道: </span>
                          <span className="font-medium">{scanData.recommendations?.current_channel || 0}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">信号: </span>
                          <span className={`font-medium ${getSignalColor(scanData.current_wifi.signal_strength)}`}>
                            {scanData.current_wifi.signal_strength} dBm
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 建议理由 */}
                  <div>
                    <h4 className="font-medium text-sm sm:text-base mb-2">分析结果</h4>
                    <div className="space-y-2">
                      {(scanData.recommendations?.reasons || []).map((reason, index) => (
                        <div key={index} className="flex items-start gap-2 text-xs sm:text-sm">
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-gray-700">{reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 推荐信道 */}
                  {(scanData.recommendations?.recommended_channels || []).length > 0 && (
                    <div>
                      <h4 className="font-medium text-sm sm:text-base mb-3">推荐信道</h4>
                      <div className="space-y-2 sm:space-y-3">
                        {(scanData.recommendations?.recommended_channels || []).map((rec, index) => (
                          <div 
                            key={index}
                            className="p-3 sm:p-4 border border-green-200 bg-green-50 rounded-lg"
                          >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                              <div>
                                <div className="font-medium text-sm sm:text-base">
                                  信道 {rec.channel}
                                </div>
                                <div className="text-xs sm:text-sm text-gray-600">
                                  干扰程度: {rec.interference_level.toFixed(1)}% | 
                                  网络数量: {rec.network_count}
                                </div>
                              </div>
                              <Badge className="bg-green-100 text-green-700 text-xs">
                                改善 {rec.improvement.toFixed(1)}%
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* 加载状态 */}
      {isLoading && !scanData && (
        <div className="text-center py-8 sm:py-12">
          <RefreshCw className="w-8 h-8 sm:w-12 sm:h-12 mx-auto mb-4 animate-spin text-blue-500" />
          <p className="text-sm sm:text-base text-gray-600">正在扫描WiFi网络...</p>
        </div>
      )}
    </div>
  );
};

export default WiFiScanResults; 