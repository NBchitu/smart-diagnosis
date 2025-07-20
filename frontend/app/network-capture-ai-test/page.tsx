"use client";
import React, { useState, useMemo } from "react";
import { Wifi, Globe, Zap, Video, RefreshCw, MessageCircle, Search, Filter, ChevronDown, ChevronUp, Activity, Server, Timer, AlertTriangle, Eye, BarChart3, Download, History, ToggleLeft, ToggleRight, FileText, Brain, Clock, Trash2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const PRESET_ISSUES = [
  { key: "website_access", label: "网站访问问题", icon: <Globe className="w-5 h-5" />, description: "分析HTTP/HTTPS网站访问性能和问题" },
  { key: "interconnection", label: "互联互通访问", icon: <RefreshCw className="w-5 h-5" />, description: "分析跨运营商网络访问质量" },
  { key: "game_lag", label: "游戏卡顿问题", icon: <BarChart3 className="w-5 h-5" />, description: "专门分析游戏流量和服务器ISP归属" },
];

export default function NetworkCaptureAITestPage() {
  const [selected, setSelected] = useState<string | null>(null);
  const [custom, setCustom] = useState("");
  const { toast } = useToast();
  const [step, setStep] = useState<1 | 2 | 3 | 4 | 5 | 6>(1); // 步骤状态：1选择问题 2抓包 3预处理 4网站性能展示 5AI分析 6结果展示
  const [taskId, setTaskId] = useState<string | null>(null);
  const [captureStatus, setCaptureStatus] = useState<'idle' | 'capturing' | 'processing' | 'ai_analyzing' | 'done' | 'error'>('idle');
  const [captureResult, setCaptureResult] = useState<any>(null);
  const [preprocessResult, setPreprocessResult] = useState<any>(null); // 预处理结果
  const [aiAnalysisResult, setAiAnalysisResult] = useState<any>(null); // AI分析结果
  const [currentView, setCurrentView] = useState<'preprocess' | 'ai_analysis'>('preprocess'); // 当前查看的结果类型
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [defaultInterface, setDefaultInterface] = useState<string>('eth0');

  // 历史记录相关状态
  const [showHistory, setShowHistory] = useState(false);
  const [historyRecords, setHistoryRecords] = useState<any[]>([]);

  // IP信息相关状态
  const [showIPDialog, setShowIPDialog] = useState(false);
  const [selectedIP, setSelectedIP] = useState<string>('');
  const [ipInfo, setIPInfo] = useState<any>(null);
  const [ipInfoLoading, setIPInfoLoading] = useState(false);
  const [ipInfoCache, setIPInfoCache] = useState<Map<string, any>>(new Map());

  // 加载历史记录
  const loadHistoryRecords = async () => {
    try {
      const response = await fetch('/api/capture/history');
      const data = await response.json();
      if (data.success) {
        setHistoryRecords(data.records || []);
      }
    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  };

  // 保存当前抓包记录到历史
  const saveToHistory = async (result: any, taskId: string) => {
    try {
      const historyRecord = {
        task_id: taskId,
        capture_time: new Date().toISOString(),
        issue_type: selected || 'custom',
        issue_description: selected ? PRESET_ISSUES.find(issue => issue.key === selected)?.label : custom,
        preprocess_result: result,
        ai_analysis_result: result.ai_analysis || null,
        has_ai_analysis: !!result.ai_analysis
      };

      await fetch('/api/capture/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(historyRecord)
      });
    } catch (error) {
      console.error('保存历史记录失败:', error);
    }
  };

  // 下载原始数据包
  const downloadRawPackets = async (taskId: string) => {
    try {
      const response = await fetch(`/api/capture/download?task_id=${taskId}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `capture_${taskId}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pcap`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('下载失败:', response.statusText);
      }
    } catch (error) {
      console.error('下载原始数据包失败:', error);
    }
  };

  // 查询IP信息
  const queryIPInfo = async (ip: string) => {
    // 检查缓存
    if (ipInfoCache.has(ip)) {
      return ipInfoCache.get(ip);
    }

    try {
      setIPInfoLoading(true);
      const response = await fetch(`/api/ip-info?ip=${encodeURIComponent(ip)}`);
      const data = await response.json();

      if (data.success) {
        // 缓存结果
        setIPInfoCache(prev => new Map(prev.set(ip, data)));
        return data;
      } else {
        console.error('IP信息查询失败:', data.error);
        return null;
      }
    } catch (error) {
      console.error('IP信息查询错误:', error);
      return null;
    } finally {
      setIPInfoLoading(false);
    }
  };

  // 显示IP详细信息
  const showIPDetails = async (ip: string) => {
    setSelectedIP(ip);
    setShowIPDialog(true);
    setIPInfo(null);

    const info = await queryIPInfo(ip);
    if (info) {
      setIPInfo(info);
    }
  };

  // 获取IP简略信息（用于列表显示）
  const getIPSummary = (ip: string) => {
    const cached = ipInfoCache.get(ip);
    if (cached && cached.summary) {
      return `${cached.summary.isp} ${cached.summary.location}`;
    }
    return '';
  };



  // 抓包配置参数
  const [captureConfig, setCaptureConfig] = useState({
    duration: 15, // 抓包时长（秒）
    interface: 'auto', // 网络接口
    maxPackets: 10000, // 最大包数
    enableDeepAnalysis: true, // 启用深度分析
  });

  // 网站性能展示相关状态
  // const [websiteData, setWebsiteData] = useState<any>(null); // 不再需要，使用allWebsiteData
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [latencyFilter, setLatencyFilter] = useState<'all' | 'fast' | 'slow' | 'error'>('all');
  const [expandedSites, setExpandedSites] = useState<Set<string>>(new Set());
  const [showConfig, setShowConfig] = useState<boolean>(false);

  // 选中逻辑：自定义输入时取消预设选中
  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustom(e.target.value);
    setSelected(null);
  };

  // 获取默认网络接口
  React.useEffect(() => {
    const fetchDefaultInterface = async () => {
      try {
        const res = await fetch('/api/capture/interfaces');
        const data = await res.json();
        if (data.default) {
          setDefaultInterface(data.default);
        }
      } catch (e) {
        console.warn('获取默认网络接口失败，使用默认值');
      }
    };

    fetchDefaultInterface();
  }, []);

  // 下一步按钮是否可用
  const canProceed = selected || custom.trim();

  // 根据问题类型处理数据
  const processAnalysisData = (result: any) => {
    const enhanced = result?.capture_summary?.enhanced_analysis;
    if (!enhanced) return null;

    const issueType = selected || 'custom';

    if (issueType === 'website_access') {
      return processWebsiteData(enhanced);
    } else if (issueType === 'interconnection') {
      return processInterconnectionData(enhanced);
    } else if (issueType === 'game_lag') {
      return processGameData(enhanced);
    }

    return null;
  };

  // 网站访问数据处理
  const processWebsiteData = (enhanced: any) => {
    const websitesAccessed = enhanced.http_analysis?.websites_accessed || {};
    const websitePerformance = enhanced.issue_specific_insights?.website_performance || {};

    // 合并网站访问数据和性能数据
    const combinedData = Object.keys(websitesAccessed).map(domain => {
      const accessCount = websitesAccessed[domain];
      const perfData = websitePerformance[domain] || {};

      return {
        domain,
        accessCount,
        ips: perfData.ips || [],
        latency: perfData.tcp_rtt?.avg_ms || null,
        requests: perfData.requests || { total: accessCount, errors: 0, error_rate_percent: 0 },
        protocol: perfData.protocol || 'HTTPS'
      };
    });

    return combinedData.sort((a, b) => b.accessCount - a.accessCount);
  };

  // 互联互通数据处理
  const processInterconnectionData = (enhanced: any) => {
    const interconnectionData = enhanced.issue_specific_insights?.targeted_analysis || {};
    const relevantMetrics = enhanced.issue_specific_insights?.relevant_metrics || {};

    return {
      local_isp: relevantMetrics.local_isp || 'unknown',
      cross_isp_connections: relevantMetrics.cross_isp_connections || 0,
      avg_cross_isp_latency: relevantMetrics.avg_cross_isp_latency || 0,
      summary: interconnectionData.summary || '未检测到互联互通数据',
      cross_isp_analysis: interconnectionData.cross_isp_analysis || {},
      same_isp_analysis: interconnectionData.same_isp_analysis || {},
      recommendations: interconnectionData.recommendations || []
    };
  };

  // 游戏数据处理
  const processGameData = (enhanced: any) => {
    const gameData = enhanced.issue_specific_insights?.targeted_analysis || {};
    const relevantMetrics = enhanced.issue_specific_insights?.relevant_metrics || {};

    return {
      game_traffic_detected: relevantMetrics.game_traffic_detected || false,
      total_game_servers: relevantMetrics.total_game_servers || 0,
      china_mobile_servers: relevantMetrics.china_mobile_servers || 0,
      avg_latency: relevantMetrics.avg_latency || 0,
      network_quality: relevantMetrics.network_quality || 'unknown',
      summary: gameData.summary || '未检测到游戏流量',
      china_mobile_analysis: gameData.china_mobile_analysis || {},
      performance_analysis: gameData.performance_analysis || {},
      recommendations: gameData.recommendations || []
    };
  };

  // 筛选数据（根据问题类型）
  const filterAnalysisData = (data: any) => {
    const issueType = selected || 'custom';

    if (issueType === 'website_access') {
      return filterWebsiteData(data);
    } else if (issueType === 'interconnection') {
      return data; // 互联互通数据不需要筛选
    } else if (issueType === 'game_lag') {
      return data; // 游戏数据不需要筛选
    }

    return data;
  };

  // 筛选网站数据
  const filterWebsiteData = (data: any[]) => {
    if (!data) return [];

    let filtered = data;

    // 搜索筛选
    if (searchTerm) {
      filtered = filtered.filter(site =>
        site.domain.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // 延迟筛选
    if (latencyFilter !== 'all') {
      filtered = filtered.filter(site => {
        if (latencyFilter === 'fast') return site.latency && site.latency <= 50;
        if (latencyFilter === 'slow') return site.latency && site.latency > 100;
        if (latencyFilter === 'error') return site.requests.error_rate_percent > 0;
        return true;
      });
    }

    return filtered;
  };

  // 获取延迟状态
  const getLatencyStatus = (latency: number | null) => {
    if (!latency) return { text: '未测量', color: 'text-gray-500', bg: 'bg-gray-100' };
    if (latency <= 50) return { text: '快速', color: 'text-green-700', bg: 'bg-green-100' };
    if (latency <= 100) return { text: '正常', color: 'text-yellow-700', bg: 'bg-yellow-100' };
    return { text: '慢', color: 'text-red-700', bg: 'bg-red-100' };
  };

  // 数据展示界面（根据问题类型）
  const renderAnalysisDataView = () => {
    const issueType = selected || 'custom';

    // 渲染对应的分析界面
    let analysisView = null;
    if (issueType === 'website_access') {
      analysisView = renderWebsitePerformanceView();
    } else if (issueType === 'interconnection') {
      analysisView = renderInterconnectionView();
    } else if (issueType === 'game_lag') {
      analysisView = renderGameAnalysisView();
    } else {
      analysisView = renderWebsitePerformanceView(); // 默认显示
    }

    // 如果分析界面为空，显示兜底的AI分析按钮
    if (!analysisView) {
      return (
        <div className="text-center py-8">
          <div className="mb-4">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">数据预处理完成</p>
            <p className="text-sm text-gray-500">准备进行AI智能分析</p>
          </div>
          <button
            onClick={() => {
              console.log('🚀 启动AI分析 - 兜底模式');
              setStep(5);
            }}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl text-sm font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2 mx-auto"
          >
            <Eye className="w-4 h-4" />
            <span>开始AI智能分析</span>
          </button>
        </div>
      );
    }

    return analysisView;
  };

  // AI分析结果展示界面
  const renderAIAnalysisView = () => {
    if (!aiAnalysisResult?.ai_analysis) {
      return (
        <div className="text-center py-8">
          <Brain className="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600">AI分析结果不可用</p>
        </div>
      );
    }

    const analysis = aiAnalysisResult.ai_analysis.analysis;

    return (
      <div className="space-y-4">
        {/* AI分析标题 */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Brain className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-bold text-gray-900">AI智能分析结果</h3>
          </div>
          <p className="text-sm text-gray-600">基于数据包深度分析的智能诊断</p>
        </div>

        {/* 诊断结果 */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className={`w-3 h-3 rounded-full mt-1 ${
              analysis.severity === 'high' ? 'bg-red-500' :
              analysis.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
            }`}></div>
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-700 mb-1">诊断结果</div>
              <div className="text-gray-900">{analysis.diagnosis}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">可信度</div>
              <span className="text-xs font-medium">{analysis.confidence}%</span>
            </div>
          </div>
        </div>

        {/* 根本原因 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm font-medium text-blue-700 mb-2">根本原因分析</div>
          <div className="text-sm text-blue-900">{analysis.root_cause}</div>
        </div>

        {/* 关键发现 */}
        {analysis.key_findings && analysis.key_findings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="text-sm font-medium text-yellow-700 mb-2">关键发现</div>
            <ul className="text-sm text-yellow-900 space-y-1">
              {analysis.key_findings.map((finding: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-yellow-600 mt-1">•</span>
                  <span>{finding}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 建议措施 */}
        {analysis.recommendations && analysis.recommendations.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="text-sm font-medium text-green-700 mb-2">建议措施</div>
            <ul className="text-sm text-green-900 space-y-1">
              {analysis.recommendations.map((rec: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 技术详情 */}
        {analysis.technical_details && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-700 mb-2">技术详情</div>
            <div className="text-xs text-gray-600 whitespace-pre-wrap font-mono bg-white p-3 rounded border max-h-48 overflow-y-auto">
              {analysis.technical_details}
            </div>
          </div>
        )}
      </div>
    );
  };

  // 使用useMemo来计算网站数据，避免不必要的重新计算
  const allWebsiteData = useMemo(() => {
    const enhanced = captureResult?.capture_summary?.enhanced_analysis;
    if (!enhanced) return null;
    return processWebsiteData(enhanced);
  }, [captureResult?.capture_summary?.enhanced_analysis]);

  // 不再需要useEffect来更新websiteData状态，直接使用allWebsiteData

  // 使用useMemo缓存筛选结果，避免不必要的重新计算
  const filteredWebsiteList = useMemo(() => {
    if (!allWebsiteData) return [];
    return filterWebsiteData(allWebsiteData);
  }, [allWebsiteData, searchTerm, latencyFilter]);

  // 网站性能展示界面
  const renderWebsitePerformanceView = () => {
    if (!allWebsiteData) return null;

    // 如果没有任何网站数据，显示无数据界面
    if (!allWebsiteData || allWebsiteData.length === 0) {
      return (
        <div className="w-full flex flex-col items-center justify-center py-8">
          <div className="mb-4">
            <Globe className="w-10 h-10 text-gray-400" />
          </div>
          <div className="text-base font-bold text-gray-700 mb-2">未检测到网站访问</div>
          <div className="text-xs text-gray-400 text-center mb-4">
            可能是抓包时间太短或没有网站访问流量
          </div>
          <button
            onClick={() => setStep(5)}
            className="bg-blue-600 text-white px-6 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            继续AI分析
          </button>
        </div>
      );
    }

    return (
      <div className="w-full space-y-4">
        {/* 标题和统计 */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
            <div className="flex items-center">
              <BarChart3 className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-base font-bold text-blue-700">网站访问性能</h3>
            </div>
            <div className="text-xs text-gray-600 bg-white px-2 py-1 rounded-lg">
              共 {allWebsiteData.length} 个网站 {filteredWebsiteList.length !== allWebsiteData.length && `(筛选后 ${filteredWebsiteList.length} 个)`}
            </div>
          </div>

          {/* 搜索和筛选 */}
          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-blue-400" />
              <input
                type="text"
                placeholder="搜索网站域名..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-blue-200 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 bg-white shadow-sm"
              />
            </div>

            <div className="flex space-x-2 overflow-x-auto pb-1">
              {[
                { key: 'all', label: '全部', icon: Globe },
                { key: 'fast', label: '快速', icon: Zap },
                { key: 'slow', label: '慢速', icon: Timer },
                { key: 'error', label: '错误', icon: AlertTriangle }
              ].map(filter => {
                const Icon = filter.icon;
                return (
                  <button
                    key={filter.key}
                    onClick={() => setLatencyFilter(filter.key as any)}
                    className={`flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0 ${
                      latencyFilter === filter.key
                        ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md'
                        : 'bg-gray-100 text-gray-600 hover:bg-gradient-to-r hover:from-gray-200 hover:to-gray-300'
                    }`}
                  >
                    <Icon className="w-3 h-3 flex-shrink-0" />
                    <span>{filter.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* 网站列表或空状态 */}
        {filteredWebsiteList.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
            <div className="mb-4">
              <Search className="w-8 h-8 text-gray-400 mx-auto" />
            </div>
            <div className="text-sm font-medium text-gray-700 mb-2">
              {searchTerm ? '未找到匹配的网站' : '当前筛选条件下无结果'}
            </div>
            <div className="text-xs text-gray-500">
              {searchTerm ? '尝试修改搜索关键词' : '尝试切换其他筛选条件'}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
          {filteredWebsiteList.map((site, index) => {
            const latencyStatus = getLatencyStatus(site.latency);
            const isExpanded = expandedSites.has(site.domain);

            return (
              <div key={site.domain} className="bg-white border border-blue-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
                {/* 主要信息 */}
                <div
                  className="p-4 cursor-pointer hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-all duration-200"
                  onClick={() => {
                    const newExpanded = new Set(expandedSites);
                    if (isExpanded) {
                      newExpanded.delete(site.domain);
                    } else {
                      newExpanded.add(site.domain);
                    }
                    setExpandedSites(newExpanded);
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1 flex-wrap">
                        <Server className="w-4 h-4 text-blue-500 flex-shrink-0" />
                        <span className="font-medium text-gray-900 truncate">{site.domain}</span>
                        <span className={`px-2 py-0.5 rounded-lg text-xs font-medium shadow-sm ${latencyStatus.bg} ${latencyStatus.color}`}>
                          {site.latency ? `${site.latency}ms` : latencyStatus.text}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 text-xs text-gray-600 flex-wrap">
                        <span className="flex items-center bg-blue-50 px-2 py-1 rounded">
                          <Activity className="w-3 h-3 mr-1 text-blue-500" />
                          {site.accessCount} 次访问
                        </span>
                        {site.ips.length > 0 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              showIPDetails(site.ips[0]);
                            }}
                            className="flex items-center bg-gray-50 px-2 py-1 rounded font-mono hover:bg-gray-100 transition-colors cursor-pointer"
                          >
                            <Globe className="w-3 h-3 mr-1 text-gray-500" />
                            <span className="mr-1">{site.ips[0]}</span>
                            {getIPSummary(site.ips[0]) && (
                              <span className="text-xs text-gray-400 ml-1 hidden sm:inline">
                                ({getIPSummary(site.ips[0])})
                              </span>
                            )}
                          </button>
                        )}
                        {site.requests.error_rate_percent > 0 && (
                          <span className="flex items-center bg-red-50 px-2 py-1 rounded text-red-600">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            {site.requests.error_rate_percent}% 错误
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="p-1 rounded-lg bg-blue-100 hover:bg-blue-200 transition-colors">
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-blue-600" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-blue-600" />
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* 展开的详细信息 */}
                {isExpanded && (
                  <div className="border-t border-blue-100 p-4 bg-gradient-to-r from-blue-50 to-purple-50">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div className="bg-white p-3 rounded-lg shadow-sm">
                        <div className="text-blue-600 mb-1 font-medium">协议类型</div>
                        <div className="font-medium text-gray-900">{site.protocol}</div>
                      </div>

                      <div className="bg-white p-3 rounded-lg shadow-sm">
                        <div className="text-blue-600 mb-1 font-medium">请求统计</div>
                        <div className="font-medium text-gray-900">
                          {site.requests.total} 总计 / {site.requests.errors} 错误
                        </div>
                      </div>

                      {site.ips.length > 0 && (
                        <div className="col-span-1 sm:col-span-2 bg-white p-3 rounded-lg shadow-sm">
                          <div className="text-blue-600 mb-2 font-medium">IP地址</div>
                          <div className="flex flex-wrap gap-2">
                            {site.ips.map((ip: string, idx: number) => {
                              const summary = getIPSummary(ip);
                              return (
                                <div key={idx} className="flex flex-col">
                                  <button
                                    onClick={() => showIPDetails(ip)}
                                    className="bg-gradient-to-r from-blue-100 to-blue-200 text-blue-700 px-3 py-1.5 rounded-lg text-xs font-mono shadow-sm hover:from-blue-200 hover:to-blue-300 transition-all duration-200 cursor-pointer"
                                  >
                                    {ip}
                                  </button>
                                  {summary && (
                                    <div className="text-xs text-gray-500 mt-1 text-center max-w-24 truncate">
                                      {summary}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {site.latency && (
                        <div className="col-span-2">
                          <div className="text-gray-600 mb-1">性能评估</div>
                          <div className="flex items-center space-x-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  site.latency <= 50 ? 'bg-green-500' :
                                  site.latency <= 100 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${Math.min(100, (site.latency / 200) * 100)}%` }}
                              ></div>
                            </div>
                            <span className="text-xs font-medium">{latencyStatus.text}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          </div>
        )}

        {/* 继续分析按钮 */}
        <div className="text-center pt-4 pb-4">
          <button
            onClick={() => {
              console.log('🚀 启动AI分析 - 网站性能模式');
              setStep(5);
            }}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl text-sm font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200 flex items-center space-x-2 mx-auto shadow-lg hover:shadow-xl"
          >
            <Eye className="w-4 h-4" />
            <span>继续AI智能分析</span>
          </button>
          <p className="text-xs text-gray-500 mt-2">AI将深度分析网络数据并提供诊断建议</p>
        </div>
      </div>
    );
  };

  // 步骤指示器渲染
  const renderStepIndicator = () => (
    <div className="w-full mb-4">
      <ol className="flex text-xs text-gray-500 space-x-1 overflow-x-auto mb-2">
        <li className={`flex-shrink-0 font-bold ${step === 1 ? 'text-green-600' : ''}`}>1. 选择问题</li>
        <li className={`flex-shrink-0 font-bold ${step === 2 ? 'text-green-600' : ''}`}>→ 2. 抓包</li>
        <li className={`flex-shrink-0 font-bold ${step === 3 ? 'text-green-600' : ''}`}>→ 3. 预处理</li>
        <li className={`flex-shrink-0 font-bold ${step === 4 ? 'text-green-600' : ''}`}>→ 4. 数据展示</li>
        <li className={`flex-shrink-0 font-bold ${step === 5 ? 'text-green-600' : ''}`}>→ 5. AI分析</li>
        <li className={`flex-shrink-0 font-bold ${step === 6 ? 'text-green-600' : ''}`}>→ 6. 结果</li>
      </ol>
      {step > 1 && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
    </div>
  );

  // 主体内容渲染
  let mainContent = null;
  if (step === 1) {
    mainContent = (
      <>
        <div className="w-full space-y-3 mb-4">
          {PRESET_ISSUES.map((item) => (
            <button
              key={item.key}
              className={`w-full flex items-start p-4 rounded-xl border-2 text-left transition-all focus:outline-none focus:ring-2 focus:ring-green-400 ${
                selected === item.key
                  ? "border-green-500 bg-green-50 text-green-700"
                  : "border-gray-200 bg-white text-gray-700 hover:border-green-400"
              }`}
              onClick={() => {
                setSelected(item.key);
                setCustom("");
              }}
              type="button"
            >
              <span className="mr-3 mt-1">{item.icon}</span>
              <div className="flex-1">
                <div className="font-medium text-sm mb-1">{item.label}</div>
                <div className="text-xs text-gray-500">{item.description}</div>
              </div>
            </button>
          ))}
        </div>
        <div className="w-full mb-4">
          <div className="relative">
            <input
              type="text"
              className="w-full rounded-xl border-2 px-4 py-3 text-sm focus:outline-none focus:border-green-500 border-gray-200 bg-white"
              placeholder="或自定义描述您的网络问题..."
              value={custom}
              onChange={handleCustomChange}
              maxLength={50}
            />
            <MessageCircle className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
          </div>
        </div>
        {/* 抓包配置 */}
        <div className="w-full mb-4">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <Filter className="w-4 h-4 mr-2" />
              <span>抓包配置</span>
            </div>
            <ChevronDown className={`w-4 h-4 transition-transform ${showConfig ? 'rotate-180' : ''}`} />
          </button>

          {showConfig && (
            <div className="mt-3 p-4 bg-white border border-gray-200 rounded-xl space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">抓包时长</label>
                  <select
                    value={captureConfig.duration}
                    onChange={(e) => setCaptureConfig(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value={10}>10秒</option>
                    <option value={15}>15秒</option>
                    <option value={30}>30秒</option>
                    <option value={60}>1分钟</option>
                    <option value={120}>2分钟</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">最大包数</label>
                  <select
                    value={captureConfig.maxPackets}
                    onChange={(e) => setCaptureConfig(prev => ({ ...prev, maxPackets: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value={5000}>5,000包</option>
                    <option value={10000}>10,000包</option>
                    <option value={20000}>20,000包</option>
                    <option value={50000}>50,000包</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">网络接口</label>
                <select
                  value={captureConfig.interface}
                  onChange={(e) => setCaptureConfig(prev => ({ ...prev, interface: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="auto">自动选择</option>
                  <option value="eth0">以太网 (eth0)</option>
                  <option value="wlan0">无线网 (wlan0)</option>
                  <option value="en0">网络接口 (en0)</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="deepAnalysis"
                  checked={captureConfig.enableDeepAnalysis}
                  onChange={(e) => setCaptureConfig(prev => ({ ...prev, enableDeepAnalysis: e.target.checked }))}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="deepAnalysis" className="ml-2 text-xs text-gray-700">
                  启用深度分析 (包含应用层协议解析)
                </label>
              </div>

              <div className="text-xs text-gray-500 bg-blue-50 p-2 rounded space-y-1">
                <div>💡 建议：网站访问问题选择15秒，互联互通选择30秒，游戏卡顿选择60秒</div>
                <div>📝 注意：HTTPS网站可能无法完全解析，建议启用深度分析</div>
                <div>🎮 游戏分析：需要在游戏运行时进行抓包，以便识别游戏流量</div>
                <div>🔄 互联互通：会分析访问不同运营商服务器的网络质量</div>
              </div>
            </div>
          )}
        </div>
        <div className="w-full text-xs text-gray-400 text-center mb-2">选择或输入后，点击下方“下一步”</div>
      </>
    );
  } else if (step === 2) {
    mainContent = (
      <div className="w-full flex flex-col items-center justify-center py-8">
        <div className="mb-4 animate-pulse">
          <Zap className="w-10 h-10 text-green-500" />
        </div>
        <div className="text-base font-bold text-green-700 mb-2">正在自动抓包...</div>
        <div className="text-xs text-gray-400">请保持网络环境稳定，预计10秒内完成</div>
      </div>
    );
  } else if (step === 3) {
    mainContent = (
      <div className="w-full flex flex-col items-center justify-center py-8">
        <div className="mb-4 animate-pulse">
          <RefreshCw className="w-10 h-10 text-blue-500" />
        </div>
        <div className="text-base font-bold text-blue-700 mb-2">正在进行数据预处理...</div>
        <div className="text-xs text-gray-400">智能提取关键信息，压缩分析量</div>
      </div>
    );
  } else if (step === 4) {
    // 数据展示界面（根据问题类型）
    const analysisView = renderAnalysisDataView();

    mainContent = (
      <div className="w-full">
        {/* 工具栏 */}
        <div className="mb-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
          {/* 结果类型切换 */}
          <div className="mb-3">
            <span className="text-sm font-medium text-gray-700 mb-2 block">查看结果:</span>
            <div className="flex items-center bg-white rounded-lg border border-blue-200 p-1 shadow-sm">
              <button
                onClick={() => setCurrentView('preprocess')}
                className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-all duration-200 flex-1 ${
                  currentView === 'preprocess'
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <FileText className="w-3 h-3 flex-shrink-0" />
                <span className="whitespace-nowrap">预处理结果</span>
              </button>
              <button
                onClick={() => setCurrentView('ai_analysis')}
                disabled={!aiAnalysisResult}
                className={`flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-all duration-200 flex-1 ${
                  currentView === 'ai_analysis' && aiAnalysisResult
                    ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-md'
                    : aiAnalysisResult
                    ? 'text-gray-600 hover:text-purple-600 hover:bg-purple-50'
                    : 'text-gray-400 cursor-not-allowed bg-gray-50'
                }`}
              >
                <Brain className="w-3 h-3 flex-shrink-0" />
                <span className="whitespace-nowrap">
                  AI分析结果
                  {!aiAnalysisResult && <span className="text-xs ml-1">(未分析)</span>}
                </span>
              </button>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => downloadRawPackets(taskId!)}
              className="flex items-center justify-center gap-1 px-3 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg text-xs font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-sm flex-1 sm:flex-none"
            >
              <Download className="w-3 h-3 flex-shrink-0" />
              <span className="whitespace-nowrap">下载原始数据包</span>
            </button>
            <button
              onClick={() => {
                loadHistoryRecords();
                setShowHistory(true);
              }}
              className="flex items-center justify-center gap-1 px-3 py-2 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg text-xs font-medium hover:from-gray-600 hover:to-gray-700 transition-all duration-200 shadow-sm"
            >
              <History className="w-3 h-3 flex-shrink-0" />
              <span className="hidden sm:inline whitespace-nowrap">历史记录</span>
            </button>
          </div>
        </div>

        {/* 根据当前视图显示对应结果 */}
        {currentView === 'preprocess' ? analysisView : (
          aiAnalysisResult ? renderAIAnalysisView() : (
            <div className="text-center py-8">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">尚未进行AI分析</p>
              <p className="text-sm text-gray-500">请先进行AI分析以查看智能诊断结果</p>
            </div>
          )
        )}

        {/* 额外的AI分析入口 - 确保始终可用 */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-3">数据预处理完成，可以开始AI分析</p>
            <button
              onClick={() => {
                console.log('🚀 启动AI分析 - 额外入口');
                setStep(5);
              }}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg flex items-center space-x-2 mx-auto"
            >
              <Activity className="w-4 h-4" />
              <span>启动AI智能分析</span>
            </button>
          </div>
        </div>
      </div>
    );
  } else if (step === 5) {
    mainContent = (
      <div className="w-full flex flex-col items-center justify-center py-8">
        <div className="mb-4 animate-spin">
          <Globe className="w-10 h-10 text-purple-500" />
        </div>
        <div className="text-base font-bold text-purple-700 mb-2">AI智能分析中...</div>
        <div className="text-xs text-gray-400">大模型正在分析网络问题</div>
      </div>
    );
  } else if (step === 6) {
    mainContent = (
      <div className="w-full flex flex-col py-4">
        {errorMsg ? (
          <div className="text-center py-8">
            <div className="mb-4">
              <RefreshCw className="w-10 h-10 text-red-500 mx-auto" />
            </div>
            <div className="text-base font-bold text-red-700 mb-2">分析失败</div>
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl p-4">
              {errorMsg}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* AI分析结果 */}
            {captureResult?.ai_analysis?.success && (
              <div className="bg-white border border-green-200 rounded-xl p-4">
                <div className="flex items-center mb-3">
                  <MessageCircle className="w-5 h-5 text-green-600 mr-2" />
                  <h3 className="text-base font-bold text-green-700">AI智能诊断</h3>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">诊断结论</div>
                    <div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
                      {captureResult.ai_analysis.analysis.diagnosis}
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div>
                      <span className="text-xs text-gray-500">严重程度: </span>
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        captureResult.ai_analysis.analysis.severity === 'high' ? 'bg-red-100 text-red-700' :
                        captureResult.ai_analysis.analysis.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {captureResult.ai_analysis.analysis.severity}
                      </span>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">置信度: </span>
                      <span className="text-xs font-medium">{captureResult.ai_analysis.analysis.confidence}%</span>
                    </div>
                  </div>

                  {/* 关键发现 */}
                  {captureResult.ai_analysis.analysis.key_findings && captureResult.ai_analysis.analysis.key_findings.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">关键发现</div>
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <ul className="text-xs text-gray-700 space-y-1">
                          {captureResult.ai_analysis.analysis.key_findings.map((finding: string, idx: number) => (
                            <li key={idx} className="flex items-start">
                              <span className="text-yellow-600 mr-2 flex-shrink-0">⚠️</span>
                              <span className="break-words">{finding}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* 诊断线索 */}
                  {captureResult.ai_analysis.analysis.diagnostic_clues && captureResult.ai_analysis.analysis.diagnostic_clues.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">诊断线索</div>
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 max-h-48 overflow-y-auto">
                        <ul className="text-xs text-gray-700 space-y-1">
                          {captureResult.ai_analysis.analysis.diagnostic_clues.map((clue: string, idx: number) => (
                            <li key={idx} className="flex items-start">
                              <span className="text-blue-500 mr-2 flex-shrink-0">•</span>
                              <span className="break-words">{clue}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* 解决建议 */}
                  {captureResult.ai_analysis.analysis.recommendations && (
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">解决建议</div>
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <ul className="text-sm text-gray-700 space-y-2">
                          {captureResult.ai_analysis.analysis.recommendations.map((rec: string, idx: number) => (
                            <li key={idx} className="flex items-start">
                              <span className="text-green-600 mr-2 flex-shrink-0">✓</span>
                              <span className="break-words">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* 后续步骤 */}
                  {captureResult.ai_analysis.analysis.next_steps && (
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">后续步骤</div>
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                        <div className="text-xs text-gray-700">{captureResult.ai_analysis.analysis.next_steps}</div>
                      </div>
                    </div>
                  )}

                  {/* 置信度和严重程度 */}
                  <div className="flex gap-4">
                    {captureResult.ai_analysis.analysis.confidence && (
                      <div className="flex-1">
                        <div className="text-xs font-medium text-gray-600 mb-1">诊断置信度</div>
                        <div className="bg-gray-100 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${captureResult.ai_analysis.analysis.confidence}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">{captureResult.ai_analysis.analysis.confidence}%</div>
                      </div>
                    )}
                    {captureResult.ai_analysis.analysis.severity && (
                      <div className="flex-1">
                        <div className="text-xs font-medium text-gray-600 mb-1">严重程度</div>
                        <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                          captureResult.ai_analysis.analysis.severity === 'critical' ? 'bg-red-100 text-red-700' :
                          captureResult.ai_analysis.analysis.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                          captureResult.ai_analysis.analysis.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {captureResult.ai_analysis.analysis.severity === 'critical' ? '严重' :
                           captureResult.ai_analysis.analysis.severity === 'high' ? '高' :
                           captureResult.ai_analysis.analysis.severity === 'medium' ? '中' : '低'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* 抓包统计摘要 */}
            {captureResult?.capture_summary && (
              <div className="bg-white border border-gray-200 rounded-xl p-4">
                <div className="flex items-center mb-3">
                  <Zap className="w-5 h-5 text-blue-600 mr-2" />
                  <h3 className="text-base font-bold text-blue-700">抓包统计</h3>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-500">总包数: </span>
                    <span className="font-medium">{captureResult.capture_summary.statistics?.total_packets || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">文件大小: </span>
                    <span className="font-medium">{Math.round((captureResult.capture_summary.file_size || 0) / 1024)}KB</span>
                  </div>
                </div>

                {/* 协议分布 */}
                {captureResult.capture_summary.statistics?.protocols && (
                  <div className="mt-3">
                    <div className="text-sm font-medium text-gray-700 mb-2">协议分布</div>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(captureResult.capture_summary.statistics.protocols).slice(0, 5).map(([protocol, count]) => (
                        <span key={protocol} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                          {protocol}: {String(count)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 增强分析信息 */}
                {captureResult.capture_summary.enhanced_analysis && (
                  <div className="mt-4 space-y-3">
                    {/* HTTP分析 */}
                    {captureResult.capture_summary.enhanced_analysis.http_analysis && (
                      <div>
                        <div className="text-sm font-medium text-gray-700 mb-2">HTTP流量分析</div>
                        <div className="bg-gray-50 rounded-lg p-3 text-xs space-y-1">
                          {captureResult.capture_summary.enhanced_analysis.http_analysis.total_requests && (
                            <div>总HTTP请求: {captureResult.capture_summary.enhanced_analysis.http_analysis.total_requests}</div>
                          )}
                          {captureResult.capture_summary.enhanced_analysis.http_analysis.unique_domains && (
                            <div>访问域名数: {captureResult.capture_summary.enhanced_analysis.http_analysis.unique_domains}</div>
                          )}
                          {captureResult.capture_summary.enhanced_analysis.http_analysis.https_ratio && (
                            <div>HTTPS比例: {(captureResult.capture_summary.enhanced_analysis.http_analysis.https_ratio * 100).toFixed(1)}%</div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* 网络质量指标 */}
                    {captureResult.capture_summary.enhanced_analysis.network_quality && (
                      <div>
                        <div className="text-sm font-medium text-gray-700 mb-2">网络质量</div>
                        <div className="bg-gray-50 rounded-lg p-3 text-xs space-y-1">
                          {captureResult.capture_summary.enhanced_analysis.network_quality.avg_rtt && (
                            <div>平均RTT: {captureResult.capture_summary.enhanced_analysis.network_quality.avg_rtt.toFixed(1)}ms</div>
                          )}
                          {captureResult.capture_summary.enhanced_analysis.network_quality.packet_loss_rate !== undefined && (
                            <div>丢包率: {(captureResult.capture_summary.enhanced_analysis.network_quality.packet_loss_rate * 100).toFixed(2)}%</div>
                          )}
                          {captureResult.capture_summary.enhanced_analysis.network_quality.retransmissions && (
                            <div>重传次数: {captureResult.capture_summary.enhanced_analysis.network_quality.retransmissions}</div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* 重新分析按钮 */}
            <div className="text-center pt-4">
              <button
                onClick={() => {
                  setStep(1);
                  setTaskId(null);
                  setCaptureResult(null);
                  setErrorMsg(null);
                  setProgress(0);
                  setSearchTerm('');
                  setLatencyFilter('all');
                  setExpandedSites(new Set());
                }}
                className="bg-green-600 text-white px-6 py-2 rounded-xl text-sm font-medium hover:bg-green-700 transition-colors"
              >
                重新分析
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 自动流程推进（集成API）
  React.useEffect(() => {
    let polling: NodeJS.Timeout | null = null;
    if ((step === 2 || step === 3) && taskId) {
      // 轮询抓包状态 - step 2和step 3都需要轮询
      const poll = async () => {
        try {
          const res = await fetch(`/api/capture/status?task_id=${taskId}`);
          const data = await res.json();
          setCaptureStatus(data.status);
          setProgress(data.progress || 0);

          if (data.status === 'processing') {
            setStep(3);
          } else if (data.status === 'done') {
            // 数据预处理完成，获取结果并显示网站性能界面
            try {
              const resultRes = await fetch(`/api/capture/result?task_id=${taskId}`);
              const resultData = await resultRes.json();
              if (resultData.result) {
                setCaptureResult(resultData.result);
                setPreprocessResult(resultData.result); // 保存预处理结果
                setCurrentView('preprocess'); // 默认显示预处理结果
                await saveToHistory(resultData.result, taskId); // 保存到历史记录
                setStep(4); // 显示网站性能界面
              } else {
                setErrorMsg(resultData.error || '获取预处理结果失败');
                setStep(6);
              }
            } catch (e) {
              setErrorMsg('获取预处理结果失败');
              setStep(6);
            }
          } else if (data.status === 'error') {
            setErrorMsg(data.error || '抓包失败');
            setStep(6);
          }
        } catch (e) {
          setErrorMsg('抓包状态查询失败');
          setStep(6);
        }
      };
      poll();
      polling = setInterval(poll, 1200);
    }
    if (step === 5 && taskId) {
      // step 5: AI分析阶段，需要重新启动AI分析
      const startAIAnalysis = async () => {
        try {
          // 获取当前筛选的域名列表
          const filteredDomains = filteredWebsiteList.map(site => site.domain);

          console.log('🔍 当前筛选的域名:', filteredDomains);
          console.log('🔍 速度分类筛选:', latencyFilter);

          // 启动AI分析，传递筛选参数
          const aiRes = await fetch('/api/capture/analyze-ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              task_id: taskId,
              filtered_domains: filteredDomains,
              latency_filter: latencyFilter
            })
          });

          if (!aiRes.ok) {
            setErrorMsg('启动AI分析失败');
            setStep(6);
            return;
          }

          // 轮询AI分析状态
          const pollAI = async () => {
            try {
              const statusRes = await fetch(`/api/capture/status?task_id=${taskId}`);
              const statusData = await statusRes.json();
              setCaptureStatus(statusData.status);
              setProgress(statusData.progress || 0);

              if (statusData.status === 'done') {
                // AI分析完成，获取最终结果
                try {
                  const resultRes = await fetch(`/api/capture/result?task_id=${taskId}`);
                  const resultData = await resultRes.json();
                  if (resultData.result) {
                    setCaptureResult(resultData.result);
                    setAiAnalysisResult(resultData.result); // 保存AI分析结果
                    setCurrentView('ai_analysis'); // 切换到AI分析结果视图
                    // 更新历史记录中的AI分析结果
                    await saveToHistory(resultData.result, taskId);
                    setStep(6);
                  } else {
                    setErrorMsg(resultData.error || '获取AI分析结果失败');
                    setStep(6);
                  }
                } catch (e) {
                  setErrorMsg('获取AI分析结果失败');
                  setStep(6);
                }
              } else if (statusData.status === 'error') {
                setErrorMsg(statusData.error || 'AI分析失败');
                setStep(6);
              }
            } catch (e) {
              setErrorMsg('AI分析状态查询失败');
              setStep(6);
            }
          };

          pollAI();
          polling = setInterval(pollAI, 2000);

        } catch (e) {
          setErrorMsg('启动AI分析失败');
          setStep(6);
        }
      };

      startAIAnalysis();
    }
    return () => {
      if (polling) clearInterval(polling);
    };
  }, [step, taskId]);

  // 预加载IP信息
  React.useEffect(() => {
    if (captureResult?.capture_summary?.enhanced_analysis) {
      const enhanced = captureResult.capture_summary.enhanced_analysis;
      const allIPs = new Set<string>();

      // 收集所有IP地址
      if (enhanced.website_performance) {
        Object.values(enhanced.website_performance).forEach((site: any) => {
          if (site.ips) {
            site.ips.forEach((ip: string) => allIPs.add(ip));
          }
        });
      }

      // 预加载IP信息（限制并发数量）
      const ipArray = Array.from(allIPs).slice(0, 10); // 限制最多10个IP
      ipArray.forEach(ip => {
        if (!ipInfoCache.has(ip)) {
          queryIPInfo(ip);
        }
      });
    }
  }, [captureResult]);



  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* 顶部栏 */}
      <header className="flex-shrink-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-bold text-gray-900">网络抓包+AI分析调测</h1>
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              loadHistoryRecords();
              setShowHistory(true);
            }}
            className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg text-sm font-medium hover:from-blue-600 hover:to-purple-600 transition-all duration-200 shadow-sm"
          >
            <History className="w-4 h-4" />
            <span className="hidden sm:inline">历史记录</span>
          </button>
          <span className="text-xs text-gray-400">实验功能</span>
        </div>
      </header>

      {/* 步骤指示 */}
      <div className="flex-shrink-0 w-full mt-2 px-2">
        {renderStepIndicator()}
      </div>

      {/* 主体内容区 */}
      <main className="flex-1 flex flex-col items-center justify-start px-2 py-2 max-w-md mx-auto w-full overflow-y-auto">
        {mainContent}

        {/* 下一步按钮，在step 1时显示在内容区域内 */}
        {step === 1 && (
          <div className="w-full mt-6 mb-4">
            <button
              className={`w-full max-w-md rounded-xl py-3 text-base font-bold transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-green-400 ${
                canProceed
                  ? "bg-green-600 text-white hover:bg-green-700"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}
              disabled={!canProceed}
              onClick={async () => {
              // toast({
              //   title: "已选择问题类型",
              //   description: selected
              //     ? PRESET_ISSUES.find((i) => i.key === selected)?.label
              //     : custom,
              //   duration: 2000,
              // });
              // 发起抓包API
              try {
                const res = await fetch('/api/capture', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    issue_type: selected || 'custom',
                    duration: captureConfig.duration,
                    interface: captureConfig.interface === 'auto' ? defaultInterface : captureConfig.interface,
                    max_packets: captureConfig.maxPackets,
                    enable_deep_analysis: captureConfig.enableDeepAnalysis,
                    user_description: custom || (selected ? PRESET_ISSUES.find(i => i.key === selected)?.label : ''),
                    enable_ai_analysis: false, // 先不进行AI分析，只做数据预处理
                  }),
                });
                const data = await res.json();
                if (data.task_id) {
                  setTaskId(data.task_id);
                  setStep(2);
                } else {
                  setErrorMsg('抓包任务创建失败');
                  setStep(5);
                }
              } catch (e) {
                setErrorMsg('抓包API请求失败');
                setStep(5);
              }
            }}
          >
            下一步
          </button>
        </div>
        )}
      </main>

      {/* 历史记录对话框 */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden">
            {/* 头部 */}
            <div className="flex items-center justify-between p-4 border-b border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">抓包历史记录</h3>
                <span className="text-sm text-gray-500 hidden sm:inline">({historyRecords.length}/10)</span>
              </div>
              <button
                onClick={() => setShowHistory(false)}
                className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
              >
                <span className="text-gray-500 text-lg">✕</span>
              </button>
            </div>

            {/* 历史记录列表 */}
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {historyRecords.length === 0 ? (
                <div className="text-center py-8">
                  <History className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">暂无历史记录</p>
                  <p className="text-sm text-gray-500">完成抓包分析后会自动保存记录</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {historyRecords.map((record, index) => (
                    <div key={record.task_id} className="border border-blue-200 rounded-xl p-4 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-all duration-200 shadow-sm">
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
                            <Clock className="w-4 h-4 text-blue-500 flex-shrink-0" />
                            <span className="text-sm font-medium text-gray-900">
                              {new Date(record.capture_time).toLocaleString('zh-CN')}
                            </span>
                            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">#{record.task_id.slice(-8)}</span>
                          </div>

                          <div className="text-sm text-gray-700 mb-2">
                            <span className="font-medium text-blue-600">问题类型:</span> {record.issue_description}
                          </div>

                          <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
                            <div className="flex items-center gap-1 bg-green-50 px-2 py-1 rounded">
                              <FileText className="w-3 h-3 text-green-600" />
                              <span className="text-green-700">预处理: 已完成</span>
                            </div>
                            <div className={`flex items-center gap-1 px-2 py-1 rounded ${
                              record.has_ai_analysis
                                ? 'bg-purple-50 text-purple-700'
                                : 'bg-gray-50 text-gray-500'
                            }`}>
                              <Brain className={`w-3 h-3 ${record.has_ai_analysis ? 'text-purple-600' : 'text-gray-400'}`} />
                              <span>AI分析: {record.has_ai_analysis ? '已完成' : '未分析'}</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 flex-shrink-0">
                          <button
                            onClick={() => {
                              // 加载历史记录的预处理结果
                              setCaptureResult(record.preprocess_result);
                              setPreprocessResult(record.preprocess_result);
                              if (record.ai_analysis_result) {
                                setAiAnalysisResult(record.ai_analysis_result);
                              }
                              setCurrentView('preprocess');
                              setTaskId(record.task_id);
                              setStep(4);
                              setShowHistory(false);
                            }}
                            className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg text-xs font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-sm"
                          >
                            <Eye className="w-3 h-3 flex-shrink-0" />
                            <span className="whitespace-nowrap">查看</span>
                          </button>
                          <button
                            onClick={() => downloadRawPackets(record.task_id)}
                            className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg text-xs font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-sm"
                          >
                            <Download className="w-3 h-3 flex-shrink-0" />
                            <span className="whitespace-nowrap">下载</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 底部操作 */}
            <div className="p-4 border-t border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="text-sm text-gray-600">
                  系统自动保存最近10次抓包记录
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setHistoryRecords([]);
                      setShowHistory(false);
                    }}
                    className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg text-sm font-medium hover:from-red-600 hover:to-red-700 transition-all duration-200 shadow-sm"
                  >
                    <Trash2 className="w-3 h-3 flex-shrink-0" />
                    <span className="whitespace-nowrap">清空记录</span>
                  </button>
                  <button
                    onClick={() => setShowHistory(false)}
                    className="px-4 py-1.5 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg text-sm font-medium hover:from-gray-600 hover:to-gray-700 transition-all duration-200 shadow-sm"
                  >
                    关闭
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* IP详细信息对话框 */}
      {showIPDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden">
            {/* 头部 */}
            <div className="flex items-center justify-between p-4 border-b border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">IP地址信息</h3>
              </div>
              <button
                onClick={() => setShowIPDialog(false)}
                className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
              >
                <span className="text-gray-500 text-lg">✕</span>
              </button>
            </div>

            {/* 内容 */}
            <div className="p-4">
              {/* IP地址 */}
              <div className="mb-4 text-center">
                <div className="text-sm text-gray-600 mb-1">IP地址</div>
                <div className="text-lg font-mono font-bold text-blue-600 bg-blue-50 px-3 py-2 rounded-lg">
                  {selectedIP}
                </div>
              </div>

              {/* 加载状态 */}
              {ipInfoLoading && (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                  <p className="text-gray-600 text-sm">正在查询IP信息...</p>
                </div>
              )}

              {/* IP信息 */}
              {ipInfo && !ipInfoLoading && (
                <div className="space-y-3">
                  {/* 基本信息 */}
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-lg">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-gray-600 mb-1">国家</div>
                        <div className="font-medium">{ipInfo.info.country || '未知'}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 mb-1">省份</div>
                        <div className="font-medium">{ipInfo.info.province || '未知'}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 mb-1">城市</div>
                        <div className="font-medium">{ipInfo.info.city || '未知'}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 mb-1">区县</div>
                        <div className="font-medium">{ipInfo.info.district || '未知'}</div>
                      </div>
                    </div>
                  </div>

                  {/* 网络信息 */}
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="grid grid-cols-1 gap-3 text-sm">
                      <div>
                        <div className="text-gray-600 mb-1">运营商</div>
                        <div className="font-medium text-green-700">{ipInfo.info.isp || '未知'}</div>
                      </div>
                      {ipInfo.info.networkType && (
                        <div>
                          <div className="text-gray-600 mb-1">网络类型</div>
                          <div className="font-medium">{ipInfo.info.networkType}</div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 其他信息 */}
                  {(ipInfo.info.zipCode || ipInfo.info.areaCode) && (
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {ipInfo.info.zipCode && (
                          <div>
                            <div className="text-gray-600 mb-1">邮政编码</div>
                            <div className="font-medium">{ipInfo.info.zipCode}</div>
                          </div>
                        )}
                        {ipInfo.info.areaCode && (
                          <div>
                            <div className="text-gray-600 mb-1">区号</div>
                            <div className="font-medium">{ipInfo.info.areaCode}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 查询失败 */}
              {!ipInfo && !ipInfoLoading && (
                <div className="text-center py-8">
                  <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">无法获取IP信息</p>
                  <p className="text-sm text-gray-500">请稍后重试</p>
                </div>
              )}
            </div>

            {/* 底部 */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => setShowIPDialog(false)}
                className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg text-sm font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );

  // 互联互通展示界面
  function renderInterconnectionView() {
    const enhanced = captureResult?.capture_summary?.enhanced_analysis;
    if (!enhanced) return null;

    const interconnectionData = processInterconnectionData(enhanced);

    if (!interconnectionData) {
      return (
        <div className="w-full flex flex-col items-center justify-center py-8">
          <div className="mb-4">
            <RefreshCw className="w-10 h-10 text-gray-400" />
          </div>
          <div className="text-base font-bold text-gray-700 mb-2">未检测到互联互通数据</div>
          <div className="text-xs text-gray-400 text-center mb-4">
            可能是抓包时间太短或没有跨运营商访问流量
          </div>
          <button
            onClick={() => setStep(5)}
            className="bg-blue-600 text-white px-6 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            继续AI分析
          </button>
        </div>
      );
    }

    return (
      <div className="w-full space-y-4">
        {/* 标题和统计 */}
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <RefreshCw className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-base font-bold text-blue-700">互联互通分析</h3>
            </div>
          </div>

          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">本地ISP</div>
                <div className="font-medium">{interconnectionData.local_isp}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">跨网连接</div>
                <div className="font-medium">{interconnectionData.cross_isp_connections} 个</div>
              </div>
            </div>

            {interconnectionData.avg_cross_isp_latency > 0 && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">跨网平均延迟</div>
                <div className="font-medium">{interconnectionData.avg_cross_isp_latency.toFixed(1)} ms</div>
              </div>
            )}
          </div>
        </div>

        {/* 分析摘要 */}
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center mb-3">
            <BarChart3 className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-base font-bold text-green-700">分析摘要</h3>
          </div>
          <div className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
            {interconnectionData.summary}
          </div>
        </div>

        {/* 优化建议 */}
        {interconnectionData.recommendations && interconnectionData.recommendations.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex items-center mb-3">
              <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
              <h3 className="text-base font-bold text-orange-700">优化建议</h3>
            </div>
            <div className="space-y-2">
              {interconnectionData.recommendations.map((rec: string, idx: number) => (
                <div key={idx} className="flex items-start text-sm">
                  <span className="text-orange-600 mr-2 flex-shrink-0">•</span>
                  <span className="text-gray-700">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 继续按钮 */}
        <div className="flex flex-col items-center pt-4 pb-4">
          <button
            onClick={() => {
              console.log('🚀 启动AI分析 - 互联互通模式');
              setStep(5);
            }}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-xl text-sm font-medium hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
          >
            <Activity className="w-4 h-4" />
            <span>继续AI分析</span>
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">AI将分析跨运营商连接质量</p>
        </div>
      </div>
    );
  }

  // 游戏分析展示界面
  function renderGameAnalysisView() {
    const enhanced = captureResult?.capture_summary?.enhanced_analysis;
    if (!enhanced) return null;

    const gameData = processGameData(enhanced);

    if (!gameData || !gameData.game_traffic_detected) {
      return (
        <div className="w-full flex flex-col items-center justify-center py-8">
          <div className="mb-4">
            <BarChart3 className="w-10 h-10 text-gray-400" />
          </div>
          <div className="text-base font-bold text-gray-700 mb-2">未检测到游戏流量</div>
          <div className="text-xs text-gray-400 text-center mb-4">
            请确认在游戏运行时进行抓包，或延长抓包时间
          </div>
          <button
            onClick={() => setStep(5)}
            className="bg-blue-600 text-white px-6 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            继续AI分析
          </button>
        </div>
      );
    }

    return (
      <div className="w-full space-y-4">
        {/* 标题和统计 */}
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <BarChart3 className="w-5 h-5 text-purple-600 mr-2" />
              <h3 className="text-base font-bold text-purple-700">游戏网络分析</h3>
            </div>
          </div>

          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">游戏服务器</div>
                <div className="font-medium">{gameData.total_game_servers} 个</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">移动服务器</div>
                <div className="font-medium text-green-600">{gameData.china_mobile_servers} 个</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">平均延迟</div>
                <div className="font-medium">{gameData.avg_latency.toFixed(1)} ms</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-600 mb-1">网络质量</div>
                <div className={`font-medium ${
                  gameData.network_quality === '优秀' ? 'text-green-600' :
                  gameData.network_quality === '良好' ? 'text-blue-600' :
                  gameData.network_quality === '一般' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {gameData.network_quality}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 分析摘要 */}
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center mb-3">
            <Activity className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-base font-bold text-green-700">分析摘要</h3>
          </div>
          <div className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
            {gameData.summary}
          </div>
        </div>

        {/* 中国移动分析 */}
        {gameData.china_mobile_analysis && Object.keys(gameData.china_mobile_analysis).length > 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex items-center mb-3">
              <Server className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-base font-bold text-blue-700">ISP分析</h3>
            </div>
            <div className="space-y-2 text-sm">
              {gameData.china_mobile_analysis.china_mobile_ratio !== undefined && (
                <div className="flex justify-between">
                  <span className="text-gray-600">移动服务器占比:</span>
                  <span className="font-medium">{(gameData.china_mobile_analysis.china_mobile_ratio * 100).toFixed(1)}%</span>
                </div>
              )}
              {gameData.china_mobile_analysis.recommendation && (
                <div className="bg-blue-50 rounded-lg p-3 text-blue-700">
                  {gameData.china_mobile_analysis.recommendation}
                </div>
              )}
            </div>
          </div>
        )}

        {/* 优化建议 */}
        {gameData.recommendations && gameData.recommendations.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex items-center mb-3">
              <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
              <h3 className="text-base font-bold text-orange-700">优化建议</h3>
            </div>
            <div className="space-y-2">
              {gameData.recommendations.map((rec: string, idx: number) => (
                <div key={idx} className="flex items-start text-sm">
                  <span className="text-orange-600 mr-2 flex-shrink-0">•</span>
                  <span className="text-gray-700">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 继续按钮 */}
        <div className="flex flex-col items-center pt-4 pb-4">
          <button
            onClick={() => {
              console.log('🚀 启动AI分析 - 游戏性能模式');
              setStep(5);
            }}
            className="bg-gradient-to-r from-green-600 to-teal-600 text-white px-8 py-3 rounded-xl text-sm font-medium hover:from-green-700 hover:to-teal-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
          >
            <BarChart3 className="w-4 h-4" />
            <span>继续AI分析</span>
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">AI将深度分析游戏网络性能</p>
        </div>
      </div>
    );
  }
}