'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Clock, 
  Settings, 
  ChevronDown, 
  ChevronUp,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

// 工具推荐数据接口
interface ToolRecommendation {
  id: string;
  name: string;
  description: string;
  category: 'network' | 'wifi' | 'connectivity' | 'gateway' | 'packet' | 'diagnosis';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  estimatedDuration: string;
  parameters: {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    defaultValue?: any;
    options?: string[];
    required: boolean;
    description: string;
  }[];
  apiEndpoint: string;
  examples: string[];
}

interface ToolRecommendationCardProps {
  recommendation: ToolRecommendation;
  onExecute?: (toolId: string, parameters: Record<string, any>) => void;
  onResult?: (toolId: string, result: any) => void;
  onPacketCaptureOpen?: () => void; // 新增：数据包分析对话框打开回调
  disabled?: boolean;
}

export function ToolRecommendationCard({
  recommendation,
  onExecute,
  onResult,
  onPacketCaptureOpen,
  disabled = false
}: ToolRecommendationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [parameters, setParameters] = useState<Record<string, any>>(() => {
    const defaultParams: Record<string, any> = {};
    recommendation.parameters.forEach(param => {
      defaultParams[param.name] = param.defaultValue;
    });
    return defaultParams;
  });

  // 获取优先级样式
  const getPriorityStyle = () => {
    switch (recommendation.priority) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      case 'low':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  // 获取优先级Badge样式
  const getPriorityBadge = () => {
    switch (recommendation.priority) {
      case 'high':
        return <Badge variant="destructive" className="text-xs">高优先级</Badge>;
      case 'medium':
        return <Badge variant="default" className="text-xs bg-yellow-600">中优先级</Badge>;
      case 'low':
        return <Badge variant="secondary" className="text-xs">低优先级</Badge>;
      default:
        return <Badge variant="outline" className="text-xs">未知</Badge>;
    }
  };

  // 执行工具
  const handleExecute = async () => {
    if (disabled || isExecuting) return;

    // 特殊处理：数据包分析工具打开全屏对话框
    if (recommendation.id === 'packet_capture' && onPacketCaptureOpen) {
      onPacketCaptureOpen();
      return;
    }

    try {
      setIsExecuting(true);
      setExecutionResult(null);

      // 通知父组件开始执行
      if (onExecute) {
        onExecute(recommendation.id, parameters);
      }

      // 调用工具API
      console.log(`🔧 执行工具: ${recommendation.name}`, {
        endpoint: recommendation.apiEndpoint,
        parameters
      });

      const response = await fetch(recommendation.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parameters),
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        setExecutionResult({
          success: true,
          data: result.data,
          timestamp: new Date().toISOString()
        });
        
        // 通知父组件执行结果
        if (onResult) {
          onResult(recommendation.id, result);
        }
      } else {
        throw new Error(result.error || '工具执行失败');
      }

    } catch (error) {
      console.error(`❌ 工具执行失败 (${recommendation.name}):`, error);
      setExecutionResult({
        success: false,
        error: (error as Error).message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsExecuting(false);
    }
  };

  // 更新参数值
  const updateParameter = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  // 渲染参数输入控件
  const renderParameterInput = (param: any) => {
    const value = parameters[param.name];

    switch (param.type) {
      case 'string':
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => updateParameter(param.name, e.target.value)}
            placeholder={param.description}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isExecuting}
          />
        );
      
      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => updateParameter(param.name, parseInt(e.target.value) || param.defaultValue)}
            placeholder={param.description}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isExecuting}
          />
        );
      
      case 'select':
        return (
          <select
            value={value || param.defaultValue}
            onChange={(e) => updateParameter(param.name, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isExecuting}
          >
            {param.options?.map((option: string) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );
      
      case 'boolean':
        return (
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => updateParameter(param.name, e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              disabled={isExecuting}
            />
            <span className="text-sm text-gray-700">{param.description}</span>
          </label>
        );
      
      default:
        return null;
    }
  };

  return (
    <Card className={cn(
      "transition-all duration-200 hover:shadow-md",
      getPriorityStyle(),
      disabled && "opacity-50 cursor-not-allowed"
    )}>
      <div className="p-4">
        {/* 卡片头部 */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">{recommendation.icon}</div>
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="font-semibold text-gray-900">{recommendation.name}</h3>
                {getPriorityBadge()}
              </div>
              <p className="text-sm text-gray-600">{recommendation.description}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center text-xs text-gray-500">
              <Clock className="w-3 h-3 mr-1" />
              {recommendation.estimatedDuration}
            </div>
          </div>
        </div>

        {/* 快速执行按钮 */}
        <div className="flex items-center justify-between mb-3">
          <Button
            onClick={handleExecute}
            disabled={disabled || isExecuting}
            size="sm"
            className="flex items-center space-x-2"
          >
            {isExecuting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{isExecuting ? '执行中...' : '立即执行'}</span>
          </Button>

          {/* 参数配置按钮 */}
          {recommendation.parameters.length > 0 && (
            <Button
              onClick={() => setIsExpanded(!isExpanded)}
              variant="outline"
              size="sm"
              className="flex items-center space-x-1"
            >
              <Settings className="w-3 h-3" />
              <span>参数</span>
              {isExpanded ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </Button>
          )}
        </div>

        {/* 展开的参数配置区域 */}
        {isExpanded && recommendation.parameters.length > 0 && (
          <div className="border-t pt-3 space-y-3">
            <h4 className="font-medium text-sm text-gray-900">参数配置</h4>
            {recommendation.parameters.map((param) => (
              <div key={param.name} className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">
                  {param.label}
                  {param.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                {renderParameterInput(param)}
                <p className="text-xs text-gray-500">{param.description}</p>
              </div>
            ))}
          </div>
        )}

        {/* 执行结果 */}
        {executionResult && (
          <div className={cn(
            "mt-3 p-3 rounded-md text-sm",
            executionResult.success 
              ? "bg-green-50 border border-green-200" 
              : "bg-red-50 border border-red-200"
          )}>
            <div className="flex items-center space-x-2 mb-2">
              {executionResult.success ? (
                <CheckCircle className="w-4 h-4 text-green-600" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-600" />
              )}
              <span className={cn(
                "font-medium",
                executionResult.success ? "text-green-800" : "text-red-800"
              )}>
                {executionResult.success ? '执行成功' : '执行失败'}
              </span>
            </div>
            
            {executionResult.success ? (
              <div className="text-green-700">
                <p>工具执行完成，查看详细结果请参考聊天记录。</p>
              </div>
            ) : (
              <div className="text-red-700">
                <p>错误: {executionResult.error}</p>
              </div>
            )}
          </div>
        )}

        {/* 示例 */}
        {recommendation.examples.length > 0 && !isExpanded && (
          <div className="mt-3 pt-3 border-t">
            <div className="text-xs text-gray-500 mb-2">常用示例:</div>
            <div className="flex flex-wrap gap-1">
              {recommendation.examples.slice(0, 3).map((example, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="text-xs cursor-pointer hover:bg-gray-100"
                  onClick={() => {
                    if (recommendation.parameters.length > 0) {
                      updateParameter(recommendation.parameters[0].name, example);
                    }
                  }}
                >
                  {example}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
} 