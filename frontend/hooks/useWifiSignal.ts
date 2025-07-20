import { useState, useEffect, useCallback, useRef } from 'react';

interface WiFiSignalData {
  ssid: string;
  signal_strength: number;
  signal_quality: number;
  channel: number;
  frequency: number;
  interface: string;
  encryption: string;
  connected: boolean;
  link_speed?: number;
  noise_level?: number;
  tx_rate?: number;
  timestamp: number;
  error?: string;
}

interface UseWifiSignalReturn {
  wifiData: WiFiSignalData | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  refreshSignal: () => Promise<void>;
  startAutoRefresh: () => void;
  stopAutoRefresh: () => void;
  isAutoRefreshing: boolean;
}

const useWifiSignal = (
  autoRefreshInterval: number = 5000, // 默认5秒更新一次
  autoStart: boolean = true
): UseWifiSignalReturn => {
  const [wifiData, setWifiData] = useState<WiFiSignalData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isAutoRefreshing, setIsAutoRefreshing] = useState<boolean>(false);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchWifiSignal = useCallback(async (): Promise<WiFiSignalData | null> => {
    // 取消之前的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await fetch('/api/wifi/signal', {
        signal: abortController.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        return result.data;
      } else {
        throw new Error(result.message || 'WiFi信号获取失败');
      }
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          return null; // 请求被取消，不视为错误
        }
        throw err;
      }
      throw new Error('未知错误');
    }
  }, []);

  const refreshSignal = useCallback(async (): Promise<void> => {
    if (isLoading) return; // 防止重复请求

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchWifiSignal();
      if (data) {
        setWifiData(data);
        setLastUpdated(new Date());
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'WiFi信号获取失败';
      setError(errorMessage);
      console.error('WiFi信号获取错误:', err);
    } finally {
      setIsLoading(false);
    }
  }, [fetchWifiSignal, isLoading]);

  const startAutoRefresh = useCallback(() => {
    if (intervalRef.current) return; // 已经在自动刷新

    setIsAutoRefreshing(true);
    
    // 立即获取一次
    refreshSignal();

    // 设置定时器
    intervalRef.current = setInterval(() => {
      refreshSignal();
    }, autoRefreshInterval);
  }, [refreshSignal, autoRefreshInterval]);

  const stopAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsAutoRefreshing(false);
  }, []);

  // 页面可见性变化处理
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // 页面隐藏时停止自动刷新
        if (isAutoRefreshing) {
          stopAutoRefresh();
        }
      } else {
        // 页面显示时恢复自动刷新
        if (autoStart) {
          startAutoRefresh();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isAutoRefreshing, autoStart, startAutoRefresh, stopAutoRefresh]);

  // 组件挂载时的初始化
  useEffect(() => {
    if (autoStart) {
      startAutoRefresh();
    }

    // 清理函数
    return () => {
      stopAutoRefresh();
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []); // 只在组件挂载时执行

  // 网络状态变化监听
  useEffect(() => {
    const handleOnline = () => {
      if (isAutoRefreshing) {
        refreshSignal();
      }
    };

    const handleOffline = () => {
      setError('网络连接断开');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [isAutoRefreshing, refreshSignal]);

  return {
    wifiData,
    isLoading,
    error,
    lastUpdated,
    refreshSignal,
    startAutoRefresh,
    stopAutoRefresh,
    isAutoRefreshing,
  };
};

export default useWifiSignal; 