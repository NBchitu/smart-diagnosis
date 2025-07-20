'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { 
  Wifi, 
  Signal, 
  Shield,
  Lock,
  Radio
} from 'lucide-react';

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

interface WiFiNetworkCardProps {
  network: WiFiNetwork;
}

const WiFiNetworkCard: React.FC<WiFiNetworkCardProps> = ({ network }) => {
  // 获取信号强度等级
  const getSignalLevel = (strength: number) => {
    if (strength >= -30) return { level: 'excellent', text: '优秀', color: 'text-green-500', bars: 4 };
    if (strength >= -50) return { level: 'good', text: '良好', color: 'text-green-400', bars: 3 };
    if (strength >= -70) return { level: 'fair', text: '一般', color: 'text-yellow-500', bars: 2 };
    return { level: 'poor', text: '较差', color: 'text-red-500', bars: 1 };
  };

  // 获取频段信息
  const getBandInfo = (frequency: number) => {
    if (frequency < 3000) {
      return { band: '2.4G', color: 'bg-blue-100 text-blue-600' };
    } else {
      return { band: '5G', color: 'bg-purple-100 text-purple-600' };
    }
  };

  // 获取加密类型信息
  const getEncryptionInfo = (encryption: string) => {
    if (encryption.includes('WPA3')) {
      return { text: 'WPA3', color: 'bg-green-100 text-green-700', icon: Shield };
    }
    if (encryption.includes('WPA2')) {
      return { text: 'WPA2', color: 'bg-blue-100 text-blue-700', icon: Shield };
    }
    if (encryption.includes('WPA')) {
      return { text: 'WPA', color: 'bg-yellow-100 text-yellow-700', icon: Lock };
    }
    if (encryption.toLowerCase().includes('open') || encryption === '') {
      return { text: 'Open', color: 'bg-red-100 text-red-700', icon: Wifi };
    }
    return { text: encryption.substring(0, 6), color: 'bg-gray-100 text-gray-700', icon: Lock };
  };

  // 渲染信号强度图标
  const renderSignalBars = (bars: number, color: string) => {
    return (
      <div className="flex items-end gap-0.5">
        {[1, 2, 3, 4].map((bar) => (
          <div
            key={bar}
            className={`w-1 rounded-sm transition-colors ${
              bar <= bars 
                ? color.replace('text-', 'bg-')
                : 'bg-gray-300'
            }`}
            style={{ height: `${bar * 3 + 2}px` }}
          />
        ))}
      </div>
    );
  };

  const signalInfo = getSignalLevel(network.signal);
  const bandInfo = getBandInfo(network.frequency);
  const encryptionInfo = getEncryptionInfo(network.encryption);
  const EncryptionIcon = encryptionInfo.icon;

  return (
    <div className="p-3 sm:p-4 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        {/* 左侧：网络信息 */}
        <div className="flex-1 min-w-0">
          {/* SSID 和频段 */}
          <div className="flex items-center gap-2 mb-2">
            <Wifi className="w-4 h-4 text-blue-500 flex-shrink-0" />
            <span className="font-medium text-sm sm:text-base truncate">
              {network.ssid || '未命名网络'}
            </span>
            <Badge className={`text-xs ${bandInfo.color}`}>
              {bandInfo.band}
            </Badge>
          </div>

          {/* BSSID */}
          <div className="text-xs text-gray-500 mb-2 font-mono">
            {network.bssid}
          </div>

          {/* 网络参数 */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs">
            {/* 信道 */}
            <div className="flex items-center gap-1">
              <Radio className="w-3 h-3 text-gray-400" />
              <span className="text-gray-600">信道</span>
              <span className="font-medium">{network.channel}</span>
            </div>

            {/* 频率 */}
            <div className="text-gray-600">
              {network.frequency} MHz
            </div>

            {/* 加密 */}
            <div className="flex items-center gap-1">
              <EncryptionIcon className="w-3 h-3 text-gray-400" />
              <Badge className={`text-xs ${encryptionInfo.color}`}>
                {encryptionInfo.text}
              </Badge>
            </div>
          </div>
        </div>

        {/* 右侧：信号强度 */}
        <div className="flex flex-col items-end gap-1">
          {/* 信号强度图标 */}
          <div className="flex items-center gap-2">
            {renderSignalBars(signalInfo.bars, signalInfo.color)}
            <span className={`text-xs font-medium ${signalInfo.color}`}>
              {signalInfo.text}
            </span>
          </div>

          {/* 信号数值 */}
          <div className="text-xs text-gray-500 text-right">
            <div>{network.signal} dBm</div>
            <div>{network.quality}%</div>
          </div>
        </div>
      </div>

      {/* 底部分割线和额外信息（当信号很强或很弱时显示提示） */}
      {(signalInfo.level === 'excellent' || signalInfo.level === 'poor') && (
        <div className="mt-3 pt-2 border-t border-gray-100">
          <div className={`text-xs p-2 rounded ${
            signalInfo.level === 'excellent' 
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}>
            {signalInfo.level === 'excellent' && '📶 信号优秀，连接体验极佳'}
            {signalInfo.level === 'poor' && '⚠️ 信号较弱，可能影响使用体验'}
          </div>
        </div>
      )}
    </div>
  );
};

export default WiFiNetworkCard; 