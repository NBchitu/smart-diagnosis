'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Wifi,
  Network,
  Shield,
  Router,
  FileSearch,
  Activity,
  Play,
  ChevronDown,
  ChevronUp,
  Loader2,
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';

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

interface StepwiseToolCardProps {
  recommendation: ToolRecommendation;
  onExecute: (toolId: string, parameters: Record<string, any>) => void;
  onPacketCaptureOpen?: () => void; // 新增：数据包分析对话框打开回调
  isLoading?: boolean;
  stepNumber?: number;
}

export function StepwiseToolCard({
  recommendation,
  onExecute,
  onPacketCaptureOpen,
  isLoading = false,
  stepNumber
}: StepwiseToolCardProps) {
  const [isParametersExpanded, setIsParametersExpanded] = useState(false);
  const [parameters, setParameters] = useState<Record<string, any>>(() => {
    const defaultParams: Record<string, any> = {};
    recommendation.parameters.forEach(param => {
      if (param.defaultValue !== undefined) {
        defaultParams[param.name] = param.defaultValue;
      }
    });
    return defaultParams;
  });

  // 获取工具图标
  const getToolIcon = () => {
    switch (recommendation.category) {
      case 'network':
        return <Network className="w-5 h-5" />;
      case 'wifi':
        return <Wifi className="w-5 h-5" />;
      case 'connectivity':
        return <Shield className="w-5 h-5" />;
      case 'gateway':
        return <Router className="w-5 h-5" />;
      case 'packet':
        return <FileSearch className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  // 获取优先级样式
  const getPriorityStyle = () => {
    switch (recommendation.priority) {
      case 'high':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'low':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  // 获取优先级Badge
  const getPriorityBadge = () => {
    switch (recommendation.priority) {
      case 'high':
        return <Badge variant="destructive" className="text-xs">高优先级</Badge>;
      case 'medium':
        return <Badge variant="default" className="bg-yellow-600 text-xs">中优先级</Badge>;
      case 'low':
        return <Badge variant="secondary" className="text-xs">低优先级</Badge>;
      default:
        return null;
    }
  };

  // 处理参数变化
  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  // 处理工具执行
  const handleExecute = () => {
    // 特殊处理：数据包分析工具打开全屏对话框
    if (recommendation.id === 'packet_capture' && onPacketCaptureOpen) {
      onPacketCaptureOpen();
      return;
    }

    // 为必需参数设置默认值
    const finalParams = { ...parameters };
    recommendation.parameters.forEach(param => {
      if (param.required && (finalParams[param.name] === undefined || finalParams[param.name] === '')) {
        finalParams[param.name] = param.defaultValue || '';
      }
    });

    onExecute(recommendation.id, finalParams);
  };

  // 渲染参数输入控件 - 移动端优化
  const renderParameterInput = (param: any) => {
    const value = parameters[param.name] ?? param.defaultValue ?? '';
    
    switch (param.type) {
      case 'string':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleParameterChange(param.name, e.target.value)}
            placeholder={param.description}
            className="w-full px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-md text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        );
      
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleParameterChange(param.name, Number(e.target.value))}
            placeholder={param.description}
            className="w-full px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-md text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        );
      
      case 'boolean':
        return (
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => handleParameterChange(param.name, e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-xs sm:text-sm text-gray-700">{param.description}</span>
          </label>
        );
      
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleParameterChange(param.name, e.target.value)}
            className="w-full px-2 sm:px-3 py-1.5 sm:py-2 border border-gray-300 rounded-md text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">选择选项</option>
            {param.options?.map((option: string) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      
      default:
        return null;
    }
  };

  return (
    <Card className={cn("border-2 transition-all", getPriorityStyle())}>
      <div className="p-2 sm:p-3">
        {/* 工具标题和信息 - 移动端优化布局 */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-2 sm:mb-3">
          <div className="flex items-start space-x-2 sm:space-x-3 mb-2 sm:mb-0">
            {stepNumber && (
              <div className="w-6 h-6 sm:w-7 sm:h-7 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-xs">{stepNumber}</span>
              </div>
            )}
            <div className="text-blue-600">
              {getToolIcon()}
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-gray-900 text-sm sm:text-base mb-1">
                {recommendation.name}
              </h4>
              <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">
                {recommendation.description}
              </p>
            </div>
          </div>
          
          <div className="flex flex-row sm:flex-col items-center sm:items-end space-x-2 sm:space-x-0 sm:space-y-2">
            {getPriorityBadge()}
            <div className="flex items-center text-xs text-gray-500">
              <Clock className="w-3 h-3 mr-1" />
              <span>{recommendation.estimatedDuration}</span>
            </div>
          </div>
        </div>

        {/* 推荐理由 - 移动端字体优化 */}
        {recommendation.reasoning && (
          <div className="mb-2 sm:mb-3 p-2 sm:p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-xs sm:text-sm text-blue-800">
              <strong>推荐理由：</strong> {recommendation.reasoning}
            </div>
          </div>
        )}

        {/* 参数配置区域 - 移动端优化 */}
        {recommendation.parameters.length > 0 && (
          <div className="mb-3 sm:mb-4">
            <Button
              onClick={() => setIsParametersExpanded(!isParametersExpanded)}
              variant="ghost"
              size="sm"
              className="w-full justify-between p-2 h-auto text-left"
            >
              <span className="font-medium text-xs sm:text-sm">
                参数配置 ({recommendation.parameters.length})
              </span>
              {isParametersExpanded ? (
                <ChevronUp className="w-3 h-3 sm:w-4 sm:h-4" />
              ) : (
                <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4" />
              )}
            </Button>
            
            {isParametersExpanded && (
              <div className="mt-2 sm:mt-3 space-y-2 sm:space-y-3 p-2 sm:p-3 bg-gray-50 rounded-lg">
                {recommendation.parameters.map((param) => (
                  <div key={param.name} className="space-y-1">
                    <label className="flex items-center justify-between text-xs sm:text-sm font-medium text-gray-700">
                      <span>
                        {param.label}
                        {param.required && <span className="text-red-500 ml-1">*</span>}
                      </span>
                    </label>
                    {renderParameterInput(param)}
                    {param.description && (
                      <p className="text-xs text-gray-500">{param.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 执行按钮 - 移动端优化 */}
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
          <Button
            onClick={handleExecute}
            disabled={isLoading}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white text-sm"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                执行中...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                立即执行
              </>
            )}
          </Button>
          
          {recommendation.parameters.length > 0 && (
            <Button
              onClick={() => setIsParametersExpanded(!isParametersExpanded)}
              variant="outline"
              size="sm"
              className="text-sm"
            >
              {isParametersExpanded ? '收起' : '配置'}
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
} 