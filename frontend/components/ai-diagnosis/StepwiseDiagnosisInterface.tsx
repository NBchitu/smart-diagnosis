'use client';

import { useRef, useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import TextareaAutosize from 'react-textarea-autosize';
import { Send, Bot, User, Loader2, ChevronRight, CheckCircle, Clock, Paperclip, Image as ImageIcon, X, Wifi, Activity, Globe, Router, Shield, BarChart3, Trash, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { StepwiseToolCard } from './StepwiseToolCard';
import { PingResultCard } from './PingResultCard';
import { PacketCaptureResultCard } from './PacketCaptureResultCard';
import { ConnectivityResultCard } from './ConnectivityResultCard';
import { WiFiScanResultCard } from './WiFiScanResultCard';
import { GatewayInfoResultCard } from './GatewayInfoResultCard';
import { ToolsPanel } from './ToolsPanel';
import { PingConfigDialog, PingConfig } from './PingConfigDialog';
import { WebsiteAccessibilityConfigDialog, WebsiteAccessibilityConfig } from './WebsiteAccessibilityConfigDialog';
import { PacketCaptureFullscreenDialog } from './PacketCaptureFullscreenDialog';
import WebsiteAccessibilityResult from './WebsiteAccessibilityResult';
import { TechWaveLoading, AdvancedWaveLoading } from '@/components/ui/wave-loading';

// 消息类型定义
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  type?: 'text' | 'analysis' | 'step_tool' | 'evaluation' | 'next_step_prompt' | 'completion' | 'tool_result' | 'loading_analysis' | 'loading_execution' | 'loading_evaluation';
  data?: any;
}

// 诊断上下文
interface DiagnosisContext {
  originalProblem: string;
  currentStep: number;
  totalSteps: number;
  executedTools: Array<{
    id: string;
    name: string;
    result: any;
    timestamp: string;
  }>;
  isComplete: boolean;
}

// 工具推荐接口
interface ToolRecommendation {
  id: string;
  name: string;
  description: string;
  category: 'network' | 'wifi' | 'connectivity' | 'gateway' | 'packet';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  estimatedDuration: string;
  parameters: Array<{
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    defaultValue?: any;
    options?: string[];
    required: boolean;
    description: string;
  }>;
  apiEndpoint: string;
  reasoning: string;
}

interface StepwiseDiagnosisInterfaceProps {
  placeholder?: string;
}

export function StepwiseDiagnosisInterface({
  placeholder = "描述您遇到的网络问题，AI将为您制定逐步诊断计划..."
}: StepwiseDiagnosisInterfaceProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const messageIdCounter = useRef(0);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [context, setContext] = useState<DiagnosisContext>({
    originalProblem: '',
    currentStep: 0,
    totalSteps: 0,
    executedTools: [],
    isComplete: false
  });

  // Ping配置对话框状态
  const [isPingDialogOpen, setIsPingDialogOpen] = useState(false);
  const [isWebsiteDialogOpen, setIsWebsiteDialogOpen] = useState(false);
  const [isPacketCaptureDialogOpen, setIsPacketCaptureDialogOpen] = useState(false);

  // 快速诊断功能按钮配置
  const quickDiagnosisButtons = [
    // 第一行：基础诊断工具
    {
      id: 'ping_test',
      name: 'Ping测试',
      icon: Activity,
      description: '测试网络连通性',
      category: 'network' as const,
      priority: 'high' as const
    },
    {
      id: 'speed_test',
      name: '网络测速',
      icon: Shield, // 临时使用，后续可添加专门的速度图标
      description: '测试上传下载速度',
      category: 'performance' as const,
      priority: 'high' as const
    },
    {
      id: 'wifi_scan',
      name: 'WiFi扫描',
      icon: Wifi,
      description: '扫描附近WiFi网络',
      category: 'wifi' as const,
      priority: 'high' as const
    },
    {
      id: 'connectivity_check',
      name: '连通性检查',
      icon: Globe,
      description: '检查网络连接状态',
      category: 'connectivity' as const,
      priority: 'high' as const
    },
    // 第二行：高级诊断工具
    {
      id: 'traceroute',
      name: '路由追踪',
      icon: Router,
      description: '追踪数据包传输路径',
      category: 'network' as const,
      priority: 'high' as const
    },
    {
      id: 'dns_test',
      name: 'DNS测试',
      icon: Globe,
      description: '测试域名解析速度',
      category: 'connectivity' as const,
      priority: 'high' as const
    },
    {
      id: 'website_accessibility_test',
      name: '网站访问测试',
      icon: Globe,
      description: '多运营商网站访问对比',
      category: 'connectivity' as const,
      priority: 'medium' as const
    },
    {
      id: 'packet_capture',
      name: '数据包分析',
      icon: BarChart3,
      description: '抓取和分析网络数据包',
      category: 'packet' as const,
      priority: 'medium' as const
    },
    // 第三行：专业工具
    {
      id: 'gateway_info',
      name: '网关信息',
      icon: Router,
      description: '获取网关配置信息',
      category: 'gateway' as const,
      priority: 'medium' as const
    },
    {
      id: 'port_scan',
      name: '端口扫描',
      icon: Shield,
      description: '检测目标主机开放端口',
      category: 'security' as const,
      priority: 'medium' as const
    },
    {
      id: 'ssl_check',
      name: 'SSL检查',
      icon: Shield,
      description: '检查网站SSL证书状态',
      category: 'security' as const,
      priority: 'medium' as const
    },
    {
      id: 'network_quality',
      name: '网络质量',
      icon: BarChart3,
      description: '持续监控网络质量',
      category: 'monitoring' as const,
      priority: 'low' as const
    }
  ];

  // 处理快速诊断按钮点击
  const handleQuickDiagnosis = async (buttonId: string) => {
    if (isLoading || isAnalyzing || context.isComplete) return;

    const button = quickDiagnosisButtons.find(b => b.id === buttonId);
    if (!button) return;

    // 特殊处理：需要配置对话框的工具
    if (buttonId === 'ping_test') {
      setIsPingDialogOpen(true);
      return;
    }

    if (buttonId === 'website_accessibility_test') {
      setIsWebsiteDialogOpen(true);
      return;
    }

    // 特殊处理：数据包分析打开全屏对话框
    if (buttonId === 'packet_capture') {
      setIsPacketCaptureDialogOpen(true);
      return;
    }

    // 特殊处理：暂未实现的新工具
    // const notImplementedTools = ['speed_test', 'traceroute', 'dns_test', 'port_scan', 'ssl_check', 'network_quality'];
    const notImplementedTools = [''];
    if (notImplementedTools.includes(buttonId)) {
      addMessage({
        role: 'assistant',
        content: `🚧 ${button.name} 功能正在开发中，敬请期待！\n\n这是一个计划中的高级诊断工具，将提供：${button.description}`,
        type: 'text'
      });
      return;
    }

    // 添加用户点击消息
    addMessage({
      role: 'user',
      content: `快速执行：${button.name}`,
      type: 'text'
    });

    // 更新上下文
    setContext(prev => ({
      ...prev,
      originalProblem: `快速执行：${button.name}`
    }));

    try {
      setIsLoading(true);

      // 直接执行工具，绕过AI分析步骤
      await handleToolExecute(buttonId, {});

    } catch (error) {
      console.error('快速诊断执行失败:', error);
      addMessage({
        role: 'assistant',
        content: '执行快速诊断时出现错误，请稍后再试。',
        type: 'text'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 处理Ping配置提交
  const handlePingSubmit = async (config: PingConfig) => {
    // 添加用户配置消息
    addMessage({
      role: 'user',
      content: `快速执行：Ping测试 (目标: ${config.target}, 次数: ${config.count})`,
      type: 'text'
    });

    // 更新上下文
    setContext(prev => ({
      ...prev,
      originalProblem: `Ping测试：${config.target}`
    }));

    try {
      setIsLoading(true);

      // 添加"测试中"提示消息
      addMessage({
        role: 'assistant',
        content: `正在对 ${config.target} 进行Ping测试，请稍候...`,
        type: 'text'
      });

      // 执行Ping测试
      await handleToolExecute('ping_test', config);

    } catch (error) {
      console.error('Ping测试执行失败:', error);
      addMessage({
        role: 'assistant',
        content: 'Ping测试执行失败，请检查网络连接或目标地址。',
        type: 'text'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 处理网站可访问性配置提交
  const handleWebsiteAccessibilitySubmit = async (config: WebsiteAccessibilityConfig) => {
    // 添加用户配置消息
    addMessage({
      role: 'user',
      content: `快速执行：网站可访问性测试 - ${config.url}`,
      type: 'text'
    });

    // 更新上下文
    setContext(prev => ({
      ...prev,
      originalProblem: `网站可访问性测试：${config.url}`
    }));

    try {
      setIsLoading(true);

      // 添加"测试中"提示消息
      addMessage({
        role: 'assistant',
        content: `正在测试 ${config.url} 的可访问性，请稍候...`,
        type: 'text'
      });

      // 执行网站可访问性测试
      await handleToolExecute('website_accessibility_test', { url: config.url });

    } catch (error) {
      console.error('网站可访问性测试执行失败:', error);
      addMessage({
        role: 'assistant',
        content: '网站可访问性测试执行失败，请检查网络连接或重试。',
        type: 'text'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 自动滚动到底部
  const scrollToBottom = useCallback(() => {
    if (scrollAreaRef.current) {
      requestAnimationFrame(() => {
        const scrollElement = scrollAreaRef.current;
        if (scrollElement) {
          // 滚动到底部
          scrollElement.scrollTo({
            top: scrollElement.scrollHeight,
            behavior: 'smooth'
          });
        }
      });
    }
  }, []);

  // 消息变化时滚动
  useEffect(() => {
    const timeoutId = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeoutId);
  }, [messages, scrollToBottom]);

  // 加载状态变化时滚动
  useEffect(() => {
    if (!isLoading && !isAnalyzing) {
      const timeoutId = setTimeout(scrollToBottom, 200);
      return () => clearTimeout(timeoutId);
    }
  }, [isLoading, isAnalyzing, scrollToBottom]);

  // 添加消息
  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const uniqueId = `${Date.now()}_${++messageIdCounter.current}_${Math.random().toString(36).substring(2, 9)}`;

    const newMessage: ChatMessage = {
      ...message,
      id: uniqueId,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  }, []);

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!input.trim() && uploadedFiles.length === 0) return;
    if (isLoading) return;

    const userMessage = input.trim();
    const files = [...uploadedFiles];

    // 清空输入和文件
    setInput('');
    setUploadedFiles([]);

    // 构建消息内容
    let messageContent = userMessage;
    if (files.length > 0) {
      const fileNames = files.map(f => f.name).join(', ');
      messageContent = userMessage ?
        `${userMessage}\n\n📎 附件: ${fileNames}` :
        `📎 上传了 ${files.length} 张图片: ${fileNames}`;
    }

    // 添加用户消息
    addMessage({
      role: 'user',
      content: messageContent,
      type: 'text',
      data: files.length > 0 ? { files: files.map(f => ({ name: f.name, type: f.type, size: f.size })) } : undefined
    });

    // 更新上下文
    setContext(prev => ({
      ...prev,
      originalProblem: userMessage || `上传了 ${files.length} 张图片`
    }));

    try {
      setIsAnalyzing(true);

      // 添加分析中的占位消息
      const analysisMessageId = addMessage({
        role: 'assistant',
        content: '正在分析您的问题并制定逐步诊断计划...',
        type: 'loading_analysis'
      });

      // 调用步进式诊断分析API
      console.log('🧠 开始步进式诊断分析...');
      const response = await fetch('/api/ai-diagnosis-stepwise', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'analyze',
          message: userMessage
        }),
      });

      if (!response.ok) {
        throw new Error('诊断分析API调用失败');
      }

      const result = await response.json();

      if (result.success && result.data) {
        // 移除分析中的占位消息
        setMessages(prev => prev.filter(msg => msg.id !== analysisMessageId));

        // 更新上下文
        setContext(prev => ({
          ...prev,
          totalSteps: result.data.totalSteps,
          currentStep: 0
        }));

        // 添加AI分析结果
        addMessage({
          role: 'assistant',
          content: result.data.analysis,
          type: 'analysis',
          data: {
            reasoning: result.data.reasoning,
            urgency: result.data.urgency,
            totalSteps: result.data.totalSteps
          }
        });

        // 自动进入第一步
        setTimeout(() => {
          handleNextStep();
        }, 1000);

      } else {
        throw new Error(result.error || '诊断分析失败');
      }

    } catch (error) {
      console.error('❌ 诊断分析失败:', error);

      // 移除分析中的消息并添加错误消息
      setMessages(prev => prev.filter(msg => !msg.content.includes('正在分析')));

      addMessage({
        role: 'assistant',
        content: `抱歉，分析您的问题时出现错误：${(error as Error).message}。请重试。`,
        type: 'text'
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 处理下一步
  const handleNextStep = async () => {
    try {
      setIsLoading(true);

      console.log('🔄 获取下一步工具推荐...');
      const response = await fetch('/api/ai-diagnosis-stepwise', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'get_next_step',
          context: context
        }),
      });

      const result = await response.json();

      if (result.success && result.data) {
        if (result.data.type === 'completion') {
          // 诊断完成
          setContext(prev => ({ ...prev, isComplete: true }));

          addMessage({
            role: 'assistant',
            content: '🎉 诊断完成！以下是完整的诊断报告：',
            type: 'text'
          });

          addMessage({
            role: 'system',
            content: result.data.finalSummary,
            type: 'completion'
          });
        } else if (result.data.type === 'next_step') {
          // 显示下一步工具
          const { currentStep, totalSteps, nextTool } = result.data;

          setContext(prev => ({
            ...prev,
            currentStep: currentStep - 1 // API返回的是1-based，这里转为0-based
          }));

          addMessage({
            role: 'assistant',
            content: `📋 第 ${currentStep}/${totalSteps} 步：${nextTool.name}`,
            type: 'text'
          });

          addMessage({
            role: 'system',
            content: nextTool.reasoning,
            type: 'step_tool',
            data: nextTool
          });
        }
      } else {
        throw new Error(result.error || '获取下一步失败');
      }

    } catch (error) {
      console.error('❌ 获取下一步失败:', error);
      addMessage({
        role: 'assistant',
        content: `获取下一步失败：${(error as Error).message}`,
        type: 'text'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 处理工具执行
  const handleToolExecute = async (toolId: string, parameters: Record<string, any>) => {
    console.log('🔧 开始执行工具:', toolId, parameters);

    const toolName = getToolName(toolId);

    // 立即设置loading状态
    setIsLoading(true);

    const executingMessageId = addMessage({
      role: 'assistant',
      content: `正在执行 ${toolName}，请稍候...`,
      type: 'loading_execution'
    });

    try {
      // 根据工具类型调用相应的API
      const apiEndpoint = getToolApiEndpoint(toolId);
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parameters),
      });

      const result = await response.json();

      // 先重置loading状态
      setIsLoading(false);

      if (result.success && result.data) {
        // 移除执行中的消息
        setMessages(prev => prev.filter(msg => msg.id !== executingMessageId));

        // 更新已执行工具列表
        const executedTool = {
          id: toolId,
          name: toolName,
          result: result.data,
          timestamp: new Date().toISOString()
        };

        setContext(prev => ({
          ...prev,
          executedTools: [...prev.executedTools, executedTool],
          currentStep: prev.currentStep + 1
        }));

        // 添加工具结果
        addMessage({
          role: 'assistant',
          content: `✅ ${toolName} 执行完成`,
          type: 'text'
        });

        addMessage({
          role: 'system',
          content: '',
          type: 'tool_result',
          data: { toolId, result: result.data }
        });

        // 请求AI评估结果（不影响工具执行状态）
        setTimeout(() => {
          handleResultEvaluation(toolId, result.data);
        }, 100);

      } else {
        throw new Error(result.error || '工具执行失败');
      }

    } catch (error) {
      console.error('❌ 工具执行失败:', error);

      // 确保重置loading状态
      setIsLoading(false);

      // 移除执行中的消息
      setMessages(prev => prev.filter(msg => msg.id !== executingMessageId));

      addMessage({
        role: 'assistant',
        content: `❌ ${toolName} 执行失败: ${(error as Error).message}`,
        type: 'text'
      });
    }
  };

  // 处理结果评估
  const handleResultEvaluation = async (toolId: string, result: any) => {
    let evaluatingMessageId: string | null = null;

    try {
      console.log('🔍 开始评估工具结果...');

      // 添加评估中的提示
      evaluatingMessageId = addMessage({
        role: 'assistant',
        content: '🤖 AI正在评估诊断结果，请稍候...',
        type: 'loading_evaluation'
      });

      const response = await fetch('/api/ai-diagnosis-stepwise', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'evaluate_result',
          context: context,
          toolResult: { toolId, result }
        }),
      });

      const evaluationResult = await response.json();

      // 移除评估中的消息
      if (evaluatingMessageId) {
        setMessages(prev => prev.filter(msg => msg.id !== evaluatingMessageId));
      }

      if (evaluationResult.success && evaluationResult.data) {
        const evaluation = evaluationResult.data.evaluation;

        // 添加评估结果
        addMessage({
          role: 'system',
          content: '',
          type: 'evaluation',
          data: evaluation
        });

        // 如果需要下一步，显示继续提示
        if (evaluation.needsNextStep && context.currentStep < context.totalSteps) {
          addMessage({
            role: 'system',
            content: '',
            type: 'next_step_prompt',
            data: { reason: evaluation.nextStepReason }
          });
        }

      } else {
        console.error('❌ 结果评估失败:', evaluationResult.error);
        addMessage({
          role: 'assistant',
          content: '⚠️ AI评估暂时不可用，但您可以继续下一步诊断',
          type: 'text'
        });
      }

    } catch (error) {
      console.error('❌ 结果评估异常:', error);

      // 移除评估中的消息
      if (evaluatingMessageId) {
        setMessages(prev => prev.filter(msg => msg.id !== evaluatingMessageId));
      }

      addMessage({
        role: 'assistant',
        content: '⚠️ AI评估遇到问题，但您可以继续下一步诊断',
        type: 'text'
      });
    }
  };

  // 处理输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (formRef.current) {
        formRef.current.requestSubmit();
      }
    }
  };

  // 文件上传处理
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length !== files.length) {
      alert('请只上传图片文件');
      return;
    }

    setUploadedFiles(prev => [...prev, ...imageFiles]);

    // 清空文件输入
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 移除上传的文件
  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // 打开文件选择器
  const openFileSelector = () => {
    fileInputRef.current?.click();
  };

  // 获取工具名称
  const getToolName = (toolId: string): string => {
    const toolNames: Record<string, string> = {
      // 现有工具
      ping: 'Ping测试',
      ping_test: 'Ping测试',
      wifi_scan: 'WiFi扫描',
      connectivity_check: '连通性检查',
      gateway_info: '网关信息',
      packet_capture: '数据包分析',
      website_accessibility_test: '网站可访问性测试',
      // 新增工具
      speed_test: '网络测速',
      traceroute: '路由追踪',
      dns_test: 'DNS测试',
      port_scan: '端口扫描',
      ssl_check: 'SSL检查',
      network_quality: '网络质量监控',
      bandwidth_analysis: '带宽使用分析',
      device_discovery: '网络设备发现',
      config_check: '网络配置检查'
    };
    return toolNames[toolId] || toolId;
  };

  // 获取工具API端点
  const getToolApiEndpoint = (toolId: string): string => {
    const endpoints: Record<string, string> = {
      // 现有工具
      ping: '/api/network-ping',
      ping_test: '/api/network-ping',
      wifi_scan: '/api/wifi-scan',
      connectivity_check: '/api/connectivity-check',
      gateway_info: '/api/gateway-info',
      packet_capture: '/api/packet-capture',
      website_accessibility_test: '/api/website-accessibility-test',
      // 新增工具 (待实现)
      speed_test: '/api/speed-test',
      traceroute: '/api/traceroute',
      dns_test: '/api/dns-test',
      port_scan: '/api/port-scan',
      ssl_check: '/api/ssl-check',
      network_quality: '/api/network-quality',
      bandwidth_analysis: '/api/bandwidth-analysis',
      device_discovery: '/api/device-discovery',
      config_check: '/api/config-check'
    };
    return endpoints[toolId] || '/api/unknown';
  };

  // 渲染消息
  const renderMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user';

    return (
      <div
        key={message.id}
        className={cn(
          "px-2 py-1 sm:px-3 sm:py-2",
          isUser ? "flex justify-end" : ""
        )}
      >
        {/* 用户消息 */}
        {isUser && (
          <div className="max-w-[280px] sm:max-w-sm md:max-w-md bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl p-3 shadow-lg shadow-blue-500/25 backdrop-blur-xl">
            <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
          </div>
        )}

        {/* AI消息 */}
        {!isUser && (
          <div className="flex gap-2 sm:gap-3">
            {/* 头像 */}
            <div className="flex-shrink-0">
              <div className="w-7 h-7 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Bot className="w-4 h-4 text-white" />
              </div>
            </div>

            {/* 消息内容 */}
            <div className="flex-1  sm:max-w-sm md:max-w-md">
              {message.type === 'text' && (
                <div className="bg-white/70 backdrop-blur-xl rounded-2xl p-3 shadow-lg shadow-black/5 border border-white/20">
                  <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">{message.content}</div>
                </div>
              )}

              {message.type === 'analysis' && (
                <div className="bg-gradient-to-br from-blue-50/80 to-indigo-50/80 backdrop-blur-xl border border-blue-200/50 rounded-2xl p-3 sm:p-4 shadow-lg shadow-blue-500/10">
                  <div className="flex items-center gap-2 mb-2 sm:mb-3">
                    <div className="w-5 h-5 sm:w-6 sm:h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                    </div>
                    <span className="font-semibold text-blue-800 text-xs sm:text-sm">AI 问题分析</span>
                  </div>
                  <div className="text-blue-700 mb-2 sm:mb-3 text-xs sm:text-sm leading-relaxed">{message.content}</div>
                  {message.data && (
                    <div className="text-xs space-y-1">
                      <div className="flex items-start gap-1">
                        <span className="text-blue-600 flex-shrink-0">诊断思路：</span>
                        <span className="text-blue-800 flex-1">{message.data.reasoning}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-blue-600 flex-shrink-0">紧急程度：</span>
                        <span className={cn(
                          "px-1.5 py-0.5 rounded text-xs font-medium",
                          message.data.urgency === 'high' ? 'bg-red-100 text-red-700' :
                            message.data.urgency === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                        )}>
                          {message.data.urgency === 'high' ? '高' :
                            message.data.urgency === 'medium' ? '中' : '低'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-blue-600 flex-shrink-0">计划步骤：</span>
                        <span className="text-blue-800">{message.data.totalSteps} 步</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {message.type === 'step_tool' && (
                <div className="bg-gradient-to-br from-emerald-50/80 to-green-50/80 backdrop-blur-xl border border-emerald-200/50 rounded-2xl p-3 sm:p-4 shadow-lg shadow-emerald-500/10">
                  <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-r from-emerald-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/25">
                      <span className="text-white font-bold text-xs sm:text-sm">
                        {context.currentStep + 1}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-emerald-800 text-xs sm:text-sm truncate">
                        {message.data.name}
                      </div>
                      <div className="text-xs sm:text-sm text-emerald-600 truncate">
                        {message.data.description}
                      </div>
                    </div>
                  </div>

                  <div className="text-emerald-700 mb-2 sm:mb-3 text-xs sm:text-sm leading-relaxed">{message.content}</div>

                  <StepwiseToolCard
                    recommendation={message.data}
                    onExecute={handleToolExecute}
                    onPacketCaptureOpen={() => setIsPacketCaptureDialogOpen(true)}
                    isLoading={isLoading}
                    stepNumber={context.currentStep + 1}
                  />
                </div>
              )}

              {message.type === 'tool_result' && (
                <div className="mt-3">
                  {(message.data.toolId === 'ping' || message.data.toolId === 'ping_test') && (
                    <PingResultCard result={message.data.result} />
                  )}
                  {message.data.toolId === 'connectivity_check' && (
                    <ConnectivityResultCard result={message.data.result} />
                  )}
                  {message.data.toolId === 'packet_capture' && (
                    <PacketCaptureResultCard result={message.data.result} />
                  )}
                  {message.data.toolId === 'wifi_scan' && (
                    <WiFiScanResultCard result={message.data.result} />
                  )}
                  {message.data.toolId === 'website_accessibility_test' && (
                    <WebsiteAccessibilityResult data={message.data.result} />
                  )}
                  {(message.data.toolId === 'gateway_info' || message.data.toolId === 'gateway_info_check') && (
                    <GatewayInfoResultCard result={message.data.result} />
                  )}
                  {/* 其他工具结果组件 */}
                </div>
              )}

              {message.type === 'evaluation' && (
                <div className="bg-gradient-to-br from-purple-50/80 to-pink-50/80 backdrop-blur-xl border border-purple-200/50 rounded-2xl p-4 shadow-lg shadow-purple-500/10 mt-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/25">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-semibold text-purple-800 text-base">AI 结果评估</span>
                  </div>

                  <div className="text-purple-700 mb-4 text-sm leading-relaxed">{message.data.summary}</div>

                  {message.data.findings && message.data.findings.length > 0 && (
                    <div className="mb-3">
                      <div className="font-medium text-purple-800 mb-2 text-sm">主要发现：</div>
                      <ul className="list-disc list-inside text-purple-700 space-y-1 text-sm">
                        {message.data.findings.map((finding: string, idx: number) => (
                          <li key={idx}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {message.data.recommendations && message.data.recommendations.length > 0 && (
                    <div>
                      <div className="font-medium text-purple-800 mb-2 text-sm">建议：</div>
                      <ul className="list-disc list-inside text-purple-700 space-y-1 text-sm">
                        {message.data.recommendations.map((rec: string, idx: number) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {message.type === 'next_step_prompt' && (
                <div className="bg-gradient-to-br from-amber-50/80 to-yellow-50/80 backdrop-blur-xl border border-amber-200/50 rounded-2xl p-4 shadow-lg shadow-amber-500/10 mt-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-amber-500 to-yellow-600 rounded-xl flex items-center justify-center shadow-lg shadow-amber-500/25">
                      <Clock className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-semibold text-amber-800 text-base">继续诊断</span>
                  </div>

                  <div className="text-yellow-700 mb-3 text-sm sm:text-base">{message.data.reason}</div>

                  <Button
                    onClick={handleNextStep}
                    disabled={isLoading}
                    className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <ChevronRight className="w-4 h-4 mr-2" />
                    )}
                    进行下一步
                  </Button>
                </div>
              )}

              {message.type === 'completion' && (
                <div className="bg-gradient-to-br from-emerald-50/80 to-green-50/80 backdrop-blur-xl border border-emerald-200/50 rounded-2xl p-4 shadow-lg shadow-emerald-500/10">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/25">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-semibold text-emerald-800 text-base">诊断完成</span>
                  </div>

                  <div className="text-emerald-700 mb-4 text-sm leading-relaxed">{message.data.summary}</div>

                  {message.data.issues && message.data.issues.length > 0 && (
                    <div className="mb-4">
                      <div className="font-medium text-emerald-800 mb-2 text-sm">发现的问题：</div>
                      <ul className="list-disc list-inside text-emerald-700 space-y-1 text-sm">
                        {message.data.issues.map((issue: string, idx: number) => (
                          <li key={idx}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {message.data.solutions && message.data.solutions.length > 0 && (
                    <div>
                      <div className="font-medium text-emerald-800 mb-2 text-sm">解决方案：</div>
                      <ul className="list-disc list-inside text-emerald-700 space-y-1 text-sm">
                        {message.data.solutions.map((solution: string, idx: number) => (
                          <li key={idx}>{solution}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* 加载动画消息类型 */}
              {message.type === 'loading_analysis' && (
                <TechWaveLoading
                  text="AI正在分析您的问题并制定诊断计划..."
                  className="my-4"
                />
              )}

              {message.type === 'loading_execution' && (
                <AdvancedWaveLoading
                  text={message.content}
                  className="my-4"
                />
              )}

              {message.type === 'loading_evaluation' && (
                <TechWaveLoading
                  text="AI正在评估诊断结果，请稍候..."
                  className="my-4"
                />
              )}
            </div>
          </div>
        )}

        {isUser && (
          <div className="flex-shrink-0">
            <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center ml-2">
              <img src="/avatar.png" className='w-5 h-5' alt="用户头像" />
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* 进度指示器 - 固定在顶部 */}
      {context.totalSteps > 0 && (
        <div className="bg-white/60 backdrop-blur-sm border-b border-white/30 p-2 sm:p-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="text-xs sm:text-sm font-medium text-gray-700">
              诊断进度: {context.currentStep + 1} / {context.totalSteps}
            </div>
            <div className="flex space-x-1.5 sm:space-x-2">
              {Array.from({ length: context.totalSteps }, (_, i) => (
                <div
                  key={i}
                  className={cn(
                    "w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full transition-all duration-500",
                    i < context.currentStep ? "bg-gradient-to-r from-green-400 to-emerald-500 shadow-lg shadow-green-400/30" :
                      i === context.currentStep ? "bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg shadow-blue-500/30 animate-pulse" :
                        "bg-gray-300/60 backdrop-blur-sm"
                  )}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 消息列表 - 可滚动区域，占据剩余空间 */}
      <div
        className="flex-1 overflow-y-auto text-gray-600 scrollbar-hide"
        ref={scrollAreaRef}
        style={{
          height: 0, // 强制flex-1生效
          minHeight: 0 // 防止内容撑开
        }}
      >
        <div className="p-3 sm:p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-full">
              <div className="relative mb-4 sm:mb-6">
                <div className="w-24 sm:w-32 rounded-3xl bg-transparent flex items-center justify-center">
                  <img src="/AIMan.png" className='w-full h-full animate-pulse' alt="AI助手" />
                </div>
              </div>
              <p className='text-sm sm:text-base font-medium text-gray-700 text-center'>
                遇到了网络问题？
                <br />
                <span className='text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 font-bold'>
                  快来试试智能排障吧！
                </span>
              </p>
            </div>
          ) : (
            <div className="space-y-3 sm:space-y-4">
              {messages.map(renderMessage)}
            </div>
          )}
        </div>
      </div>

      {/* 输入区域 - 固定在底部 */}
      <div className="border-t border-white/30 bg-white/60 backdrop-blur-sm flex-shrink-0">

        {/* 快速诊断按钮组 */}
        <div className="px-3 sm:px-4 pt-2 sm:pt-3">
          <div className="relative">
            <div className="overflow-x-auto scrollbar-hide">
              <div className="flex space-x-1.5 sm:space-x-2 pb-2">
                {/* 工具面板按钮 */}
                <ToolsPanel
                  onToolSelect={handleQuickDiagnosis}
                  disabled={isLoading || isAnalyzing || context.isComplete}
                />

                {quickDiagnosisButtons.map((button) => {
                  const IconComponent = button.icon;
                  return (
                    <Button
                      key={button.id}
                      size={"sm"}
                      onClick={() => handleQuickDiagnosis(button.id)}
                      disabled={isLoading || isAnalyzing || context.isComplete}
                      className="flex-shrink-0 group relative bg-white/70 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 border border-white/50 hover:border-blue-300/50 rounded-xl px-2.5 py-1.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md backdrop-blur-sm"
                      title={button.description}
                    >
                      <div className="flex items-center space-x-1.5">
                        <div className="p-1 bg-gradient-to-r from-blue-500/10 to-purple-500/10 group-hover:from-blue-500/20 group-hover:to-purple-500/20 rounded-lg transition-all duration-300">
                          <IconComponent className="w-3.5 h-3.5 text-gray-600 group-hover:text-blue-600 transition-colors duration-300" />
                        </div>
                        <span className="text-xs font-medium text-gray-700 group-hover:text-blue-700 whitespace-nowrap transition-colors duration-300">
                          {button.name}
                        </span>
                      </div>

                      {/* Loading状态 */}
                      {isLoading && (
                        <div className="absolute inset-0 bg-white/80 rounded-xl flex items-center justify-center">
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
                        </div>
                      )}
                    </Button>
                  );
                })}
              </div>
            </div>

            {/* 滚动提示 */}
            <div className="absolute right-0 top-0 bottom-0 w-6 bg-gradient-to-l from-white via-white/80 to-transparent pointer-events-none" />
          </div>
        </div>

        {/* 已上传的文件预览 */}
        {uploadedFiles.length > 0 && (
          <div className="px-3 sm:px-4 pt-2">
            <div className="flex flex-wrap gap-2">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="relative">
                  <div className="flex items-center gap-2 bg-gradient-to-r from-blue-50/80 to-purple-50/80 backdrop-blur-sm border border-blue-200/50 rounded-lg px-3 py-2 shadow-sm">
                    <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded flex items-center justify-center">
                      <ImageIcon className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-xs text-blue-800 max-w-24 truncate font-medium">
                      {file.name}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-blue-600 hover:text-red-600 hover:bg-red-50/70 rounded p-0.5 transition-all duration-300"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 输入框区域 */}
        <div className="p-3 sm:p-4">
          <form ref={formRef} onSubmit={handleSubmit} className="relative" suppressHydrationWarning={true}>
            {/* 隐藏的文件输入 */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
              suppressHydrationWarning={true}
            />

            {/* 主输入框容器 */}
            <div className="relative bg-white/70 backdrop-blur-xl border border-white/50 rounded-2xl overflow-hidden focus-within:border-blue-400/50 focus-within:shadow-lg focus-within:shadow-blue-500/10 transition-all duration-300">
              {/* 输入框 */}
              <TextareaAutosize
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                className="w-full min-h-[44px] max-h-28 px-4 py-3 pr-24 bg-transparent border-none focus:outline-none resize-none placeholder-gray-500 text-sm leading-relaxed"
                disabled={isLoading || isAnalyzing || context.isComplete}
                suppressHydrationWarning={true}
              />

              {/* 右侧按钮组 */}
              <div className="absolute right-2 bottom-2 flex items-center gap-1">
                {/* 清空聊天按钮 */}
                <button
                  type="button"
                  onClick={() => {
                    setMessages([]);
                    setContext({
                      originalProblem: '',
                      currentStep: 0,
                      totalSteps: 0,
                      executedTools: [],
                      isComplete: false
                    });
                    setInput('');
                    setUploadedFiles([]);
                  }}
                  disabled={messages.length === 0 && input.trim() === '' && uploadedFiles.length === 0}
                  className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50/70 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm"
                  title="清空聊天"
                >
                  <Trash className="w-3.5 h-3.5" />
                </button>

                {/* 图片上传按钮 */}
                <button
                  type="button"
                  onClick={openFileSelector}
                  disabled={isLoading || isAnalyzing || context.isComplete}
                  className="p-1.5 text-gray-500 hover:text-purple-600 hover:bg-purple-50/70 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm"
                  title="上传图片"
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                </button>

                {/* 发送按钮 */}
                <Button
                  type="submit"
                  size="sm"
                  disabled={(!input.trim() && uploadedFiles.length === 0) || isLoading || isAnalyzing || context.isComplete}
                  className="p-1.5 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25"
                >
                  {isAnalyzing ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Send className="w-3.5 h-3.5" />
                  )}
                </Button>
              </div>
            </div>

            {/* 底部提示文字 */}
            <div className="flex items-center justify-between mt-1.5 px-1">
              <div className="text-xs text-gray-400">
                {uploadedFiles.length > 0 && (
                  <span>{uploadedFiles.length} 张图片</span>
                )}
              </div>
              <div className="text-xs text-gray-400">
                Enter 发送 • Shift+Enter 换行
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Ping配置对话框 */}
      <PingConfigDialog
        isOpen={isPingDialogOpen}
        onClose={() => setIsPingDialogOpen(false)}
        onSubmit={handlePingSubmit}
      />

      {/* 网站可访问性配置对话框 */}
      <WebsiteAccessibilityConfigDialog
        isOpen={isWebsiteDialogOpen}
        onClose={() => setIsWebsiteDialogOpen(false)}
        onSubmit={handleWebsiteAccessibilitySubmit}
      />

      {/* 数据包分析全屏对话框 */}
      <PacketCaptureFullscreenDialog
        isOpen={isPacketCaptureDialogOpen}
        onClose={() => setIsPacketCaptureDialogOpen(false)}
        onMinimize={() => {
          // 可以在这里添加最小化的额外逻辑
          console.log('数据包分析对话框已最小化');
        }}
      />
    </div>
  );
}