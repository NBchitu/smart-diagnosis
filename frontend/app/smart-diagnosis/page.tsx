'use client';

import { StepwiseDiagnosisInterface } from '@/components/ai-diagnosis/StepwiseDiagnosisInterface';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Activity } from 'lucide-react';
import Link from 'next/link';

export default function SmartDiagnosisPage() {
  return (
    <div className="h-screen flex flex-col relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 safe-area-inset">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-indigo-400/10 to-pink-400/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/5 to-blue-400/5 rounded-full blur-3xl"></div>
      </div>

      {/* 浮动装饰元素 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-2 h-2 bg-blue-400/30 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-20 w-1 h-1 bg-purple-400/30 rounded-full animate-ping"></div>
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-indigo-400/20 rounded-full animate-bounce"></div>
        <div className="absolute bottom-20 right-10 w-2 h-2 bg-pink-400/30 rounded-full animate-pulse"></div>
      </div>

      {/* 固定头部 */}
      <div className="relative z-10 bg-white/70 backdrop-blur-xl border-b border-white/20 shadow-sm flex-shrink-0">
        <div className="max-w-4xl mx-auto px-3 sm:px-4 py-2.5 sm:py-3">
          <div className="flex items-center justify-between">
            {/* 返回按钮和标题 */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              <Link href="/">
                <Button variant="ghost" size="sm" className="rounded-xl hover:bg-white/50 px-2 sm:px-3">
                  <ArrowLeft className="w-4 h-4 sm:mr-2" />
                  <span className="hidden sm:inline">返回</span>
                </Button>
              </Link>
              <div className="flex items-center space-x-3">
                <div>
                  <h1 className="text-base sm:text-lg font-bold text-gray-800 tracking-tight">
                    AI 智能诊断
                  </h1>
                </div>
              </div>
            </div>

            {/* 状态标识 */}
            <div className="flex items-center space-x-3">
              <Badge variant="secondary" className="bg-green-100/60 backdrop-blur-sm border-0 text-green-700 text-xs">
                <Activity className="w-3 h-3 mr-1" />
                在线
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* 主要聊天内容区域 - 占据剩余空间 */}
      <div className="relative z-10 flex-1 overflow-hidden">
        <div className="h-full max-w-4xl mx-auto">
          <StepwiseDiagnosisInterface />
        </div>
      </div>
    </div>
  );
}