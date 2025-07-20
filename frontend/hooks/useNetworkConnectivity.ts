import { useState, useCallback } from 'react';

interface ConnectivityDetails {
  gateway_reachable: boolean;
  dns_resolution: boolean;
  external_ping: boolean;
  http_response: boolean;
}

interface GatewayInfo {
  ip: string | null;
  interface: string | null;
  reachable: boolean;
}

interface ConnectivityResult {
  local_network: boolean;
  internet_dns: boolean;
  internet_http: boolean;
  details: ConnectivityDetails;
  latency: Record<string, number>;
  gateway_info: GatewayInfo;
  status: 'excellent' | 'good' | 'limited' | 'disconnected' | 'error';
  message: string;
  timestamp: number;
}

interface UseNetworkConnectivityReturn {
  result: ConnectivityResult | null;
  isChecking: boolean;
  error: string | null;
  checkConnectivity: () => Promise<void>;
}

export function useNetworkConnectivity(): UseNetworkConnectivityReturn {
  const [result, setResult] = useState<ConnectivityResult | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkConnectivity = useCallback(async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      const response = await fetch('/api/network/connectivity-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setResult(data.data);
      } else {
        setError('检测失败: ' + (data.message || '未知错误'));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '网络检测失败');
    } finally {
      setIsChecking(false);
    }
  }, []);

  return {
    result,
    isChecking,
    error,
    checkConnectivity
  };
} 