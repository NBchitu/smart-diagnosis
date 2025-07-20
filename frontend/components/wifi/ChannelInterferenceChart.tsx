'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart3, Radio, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChannelData {
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

interface ChannelInterferenceChartProps {
  channelData: ChannelData;
  currentChannel?: number;
}

const ChannelInterferenceChart: React.FC<ChannelInterferenceChartProps> = ({
  channelData,
  currentChannel
}) => {
  // 标签页状态管理
  const [activeTab, setActiveTab] = useState<'2.4ghz' | '5ghz'>('2.4ghz');

  // 调试：输出接收到的数据
  console.log('ChannelInterferenceChart received channelData:', channelData);
  console.log('ChannelInterferenceChart received currentChannel:', currentChannel);

  // 获取干扰级别颜色
  const getInterferenceColor = (level: number) => {
    if (level >= 75) return 'bg-red-500';
    if (level >= 50) return 'bg-yellow-500';
    if (level >= 25) return 'bg-orange-400';
    return 'bg-green-500';
  };

  // 获取干扰级别文本
  const getInterferenceLevelText = (level: number) => {
    if (level >= 75) return '严重';
    if (level >= 50) return '中等';
    if (level >= 25) return '轻微';
    return '良好';
  };

  // 获取干扰级别颜色类
  const getInterferenceLevelColor = (level: number) => {
    if (level >= 75) return 'text-red-600 bg-red-50';
    if (level >= 50) return 'text-yellow-600 bg-yellow-50';
    if (level >= 25) return 'text-orange-600 bg-orange-50';
    return 'text-green-600 bg-green-50';
  };

  // 渲染频段图表
  const renderBandChart = (bandData: Record<number, any>, bandName: string, isCurrentBand: boolean) => {
    const channels = Object.keys(bandData).map(Number).sort((a, b) => a - b);
    const maxLevel = Math.max(...Object.values(bandData).map((ch: any) => ch.level), 1);

    return (
      <div className="space-y-4">
        {/* 图表容器 */}
        <div className="relative">
          {/* Y轴标签 */}
          <div className="flex flex-col justify-between text-xs text-gray-500 absolute -left-8 sm:-left-10 h-32 py-1">
            <span>100%</span>
            <span>75%</span>
            <span>50%</span>
            <span>25%</span>
            <span>0%</span>
          </div>

          {/* 图表区域 */}
          <div className="ml-4 sm:ml-6 p-3 sm:p-4 bg-gray-50 rounded-lg overflow-x-auto">
            <div className="flex items-end gap-1 sm:gap-2 min-w-max pb-2" style={{height: '128px'}}>
              {channels.map((channel) => {
                const data = bandData[channel];
                const height = Math.max((data.level / 100) * 120, 4); // 最小高度4px
                const isCurrentCh = currentChannel === channel;
                
                return (
                  <div
                    key={channel}
                    className="flex flex-col items-center group relative"
                    style={{minWidth: '24px'}}
                  >
                    {/* 柱子 */}
                    <div
                      className={`w-4 sm:w-6 rounded-t transition-all duration-200 ${
                        isCurrentCh 
                          ? 'ring-2 ring-blue-400 ring-offset-1' 
                          : ''
                      } ${getInterferenceColor(data.level)} relative`}
                      style={{ height: `${height}px` }}
                    >
                      {/* 网络数量标签 */}
                      {data.count > 0 && (
                        <div className="absolute -top-5 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-700">
                          {data.count}
                        </div>
                      )}
                    </div>
                    
                    {/* 信道号 */}
                    <div className={`text-xs mt-1 font-medium ${
                      isCurrentCh ? 'text-blue-600' : 'text-gray-600'
                    }`}>
                      {channel}
                    </div>
                    
                    {/* 悬停提示 */}
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                      <div>信道 {channel}</div>
                      <div>干扰: {data.level.toFixed(1)}%</div>
                      <div>网络: {data.count}个</div>
                      {data.avg_signal > 0 && (
                        <div>信号: {data.avg_signal.toFixed(0)} dBm</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* X轴标签 */}
            <div className="text-center text-xs text-gray-500 mt-2">
              信道
            </div>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 text-xs sm:text-sm">
          <div className="text-center p-2 bg-blue-50 rounded">
            <div className="font-medium text-blue-600">
              {Object.values(bandData).reduce((sum, ch: any) => sum + ch.count, 0)}
            </div>
            <div className="text-gray-600">总网络</div>
          </div>
          <div className="text-center p-2 bg-red-50 rounded">
            <div className="font-medium text-red-600">
              {Object.entries(bandData).filter(([_, ch]: any) => ch.level >= 75).length}
            </div>
            <div className="text-gray-600">严重干扰</div>
          </div>
          <div className="text-center p-2 bg-yellow-50 rounded">
            <div className="font-medium text-yellow-600">
              {Object.entries(bandData).filter(([_, ch]: any) => ch.level >= 50 && ch.level < 75).length}
            </div>
            <div className="text-gray-600">中等干扰</div>
          </div>
          <div className="text-center p-2 bg-green-50 rounded">
            <div className="font-medium text-green-600">
              {Object.entries(bandData).filter(([_, ch]: any) => ch.level < 25).length}
            </div>
            <div className="text-gray-600">良好信道</div>
          </div>
        </div>

        {/* 详细信道信息 */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm">信道详情</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {channels
              .filter(ch => bandData[ch].count > 0)
              .sort((a, b) => bandData[b].level - bandData[a].level)
              .slice(0, 6) // 只显示前6个
              .map((channel) => {
                const data = bandData[channel];
                const isCurrentCh = currentChannel === channel;
                
                return (
                  <div
                    key={channel}
                    className={`p-2 sm:p-3 border rounded-lg ${
                      isCurrentCh 
                        ? 'border-blue-200 bg-blue-50' 
                        : 'border-gray-200 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className={`font-medium text-sm ${
                        isCurrentCh ? 'text-blue-600' : 'text-gray-900'
                      }`}>
                        信道 {channel}
                        {isCurrentCh && <span className="text-xs ml-1">(当前)</span>}
                      </span>
                      <Badge 
                        className={`text-xs ${getInterferenceLevelColor(data.level)}`}
                        variant="outline"
                      >
                        {getInterferenceLevelText(data.level)}
                      </Badge>
                    </div>
                    
                    <div className="space-y-1 text-xs text-gray-600">
                      <div>干扰: {data.level.toFixed(1)}%</div>
                      <div>网络: {data.count}个</div>
                      {data.avg_signal > 0 && (
                        <div>平均信号: {data.avg_signal.toFixed(0)} dBm</div>
                      )}
                    </div>

                    {/* 网络列表 */}
                    {data.networks.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-100">
                        <div className="text-xs text-gray-500 mb-1">网络:</div>
                        <div className="space-y-1">
                          {data.networks.slice(0, 2).map((network: {ssid: string; signal: number}, idx: number) => (
                            <div key={idx} className="text-xs text-gray-600 truncate">
                              {network.ssid} ({network.signal} dBm)
                            </div>
                          ))}
                          {data.networks.length > 2 && (
                            <div className="text-xs text-gray-500">
                              +{data.networks.length - 2} 更多...
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* 图表标题 */}
      <div className="flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-blue-500" />
        <h2 className="text-lg sm:text-xl font-bold">信道干扰分析</h2>
      </div>

      {/* 图例 */}
      <Card>
        <CardContent className="p-3 sm:p-4">
          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-6 text-xs sm:text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span>良好 (0-25%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-400 rounded"></div>
              <span>轻微 (25-50%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span>中等 (50-75%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span>严重 (75-100%)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 频段标签页导航 */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('2.4ghz')}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-2",
            activeTab === '2.4ghz'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          )}
        >
          <Radio className="w-4 h-4" />
          2.4GHz 频段
          <Badge variant="outline" className="text-xs">
            {channelData?.summary?.total_24ghz_networks || 0}个网络
          </Badge>
        </button>
        <button
          onClick={() => setActiveTab('5ghz')}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-2",
            activeTab === '5ghz'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          )}
        >
          <Radio className="w-4 h-4" />
          5GHz 频段
          <Badge variant="outline" className="text-xs">
            {channelData?.summary?.total_5ghz_networks || 0}个网络
          </Badge>
        </button>
      </div>

      {/* 频段图表内容 */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base sm:text-lg flex items-center gap-2">
            <Radio className="w-4 h-4 sm:w-5 sm:h-5" />
            {activeTab === '2.4ghz' ? '2.4GHz' : '5GHz'} 频段分析
            {((activeTab === '2.4ghz' && currentChannel && currentChannel <= 14) || 
              (activeTab === '5ghz' && currentChannel && currentChannel > 14)) && (
              <Badge variant="outline" className="text-xs">当前频段</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* 2.4GHz 频段图表 */}
          {activeTab === '2.4ghz' && channelData?.["2.4ghz"] && renderBandChart(
            channelData["2.4ghz"], 
            "2.4GHz", 
            currentChannel ? currentChannel <= 14 : false
          )}

          {/* 5GHz 频段图表 */}
          {activeTab === '5ghz' && channelData?.["5ghz"] && Object.keys(channelData["5ghz"]).length > 0 && renderBandChart(
            channelData["5ghz"], 
            "5GHz", 
            currentChannel ? currentChannel > 14 : false
          )}

          {/* 如果5GHz数据为空的提示 */}
          {activeTab === '5ghz' && (!channelData?.["5ghz"] || Object.keys(channelData["5ghz"]).length === 0) && (
            <div className="text-center py-8 text-gray-500">
              <Radio className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>暂无5GHz频段数据</p>
              <p className="text-sm mt-1">请确保您的WiFi设备支持5GHz频段</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 总体分析 */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base sm:text-lg flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5 text-orange-500" />
            总体分析
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium text-sm">2.4GHz 频段</h4>
              <div className="text-xs sm:text-sm text-gray-600 space-y-1">
                <div>• 总网络数: {channelData?.summary?.total_24ghz_networks || 0}个</div>
                <div>• 最拥挤信道: {channelData?.summary?.most_crowded_24ghz || 0}</div>
                <div>• 最空闲信道: {channelData?.summary?.least_crowded_24ghz || 0}</div>
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-sm">5GHz 频段</h4>
              <div className="text-xs sm:text-sm text-gray-600 space-y-1">
                <div>• 总网络数: {channelData?.summary?.total_5ghz_networks || 0}个</div>
                <div>• 干扰较少，建议优先使用</div>
                <div>• 支持更高的传输速度</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChannelInterferenceChart; 