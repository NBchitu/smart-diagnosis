'use client'

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wifi, Smartphone, Shield, Zap, PocketKnife, Sparkles, Network, Activity } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);
  const [currentFeature, setCurrentFeature] = useState(0);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: <PocketKnife className="w-6 h-6" />,
      title: "瑞士军刀 装维工具集",
      description: "网络诊断利器"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "AI 智能诊断",
      description: "网络诊断专家系统"
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: "性能监控",
      description: "全方位设备状态检测"
    }
  ];



  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-indigo-400/20 to-pink-400/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/10 to-blue-400/10 rounded-full blur-3xl"></div>
      </div>

      {/* 浮动装饰元素 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-2 h-2 bg-blue-400/40 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-20 w-1 h-1 bg-purple-400/40 rounded-full animate-ping"></div>
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-indigo-400/30 rounded-full animate-bounce"></div>
        <div className="absolute bottom-20 right-10 w-2 h-2 bg-pink-400/40 rounded-full animate-pulse"></div>
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        {/* 头部状态栏 */}
        <div className="flex justify-between items-center p-4 pt-12">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-600 font-medium">系统在线</span>
          </div>
          <Badge variant="secondary" className="bg-white/60 backdrop-blur-sm border-0 text-gray-700">
            <Sparkles className="w-3 h-3 mr-1" />
            AI 驱动
          </Badge>
        </div>

        {/* 主要内容区域 */}
        <div className="flex-1 flex flex-col justify-center px-6 pb-8">
          {/* Logo 和标题 */}
          <div className={`text-center mb-12 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="relative mb-6">
              <div className="relative w-40 h-40 mx-auto bg-transparent rounded-3xl flex items-center justify-center ">
                <img src="/logo.png" className='w-full h-full bg-transparent'></img>
                <div className="absolute top-2 right-2 w-6 h-6 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              </div>

            </div>

            <h1 className="text-3xl font-bold text-gray-800 mb-3 tracking-tight">
              宽带诊断AI魔盒
            </h1>
            <p className="text-gray-600 text-lg leading-relaxed">
              专业网络监测 · 智能诊断分析
            </p>
          </div>

          {/* 功能特性卡片 */}
          <div className={`mb-12 transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <Card className="bg-white/70 backdrop-blur-xl border-0 shadow-xl shadow-black/5 rounded-3xl overflow-hidden">
              <CardContent className="p-0">
                <div className="relative h-32 flex items-center justify-center">
                  {features.map((feature, index) => (
                    <div
                      key={index}
                      className={`absolute inset-0 flex items-center justify-center transition-all duration-500 ${currentFeature === index ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
                        }`}
                    >
                      <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white">
                          {feature.icon}
                        </div>
                        <h3 className="font-semibold text-gray-800 mb-1">{feature.title}</h3>
                        <p className="text-sm text-gray-600">{feature.description}</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* 指示器 */}
                <div className="flex justify-center space-x-2 pb-6">
                  {features.map((_, index) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full transition-all duration-300 ${currentFeature === index ? 'bg-blue-500 w-6' : 'bg-gray-300'
                        }`}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 底部操作按钮 */}
          <div className={`space-y-3 transition-all duration-1000 delay-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <Link href="/smart-diagnosis" className="block">
              <Button className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-2xl shadow-lg shadow-blue-500/25 transition-all duration-300">
                <Zap className="w-5 h-5 mr-2" />
                开始使用
              </Button>
            </Link>

            <Link href="/" className="block">
              <Button variant="ghost" className="w-full h-12 text-gray-600 hover:text-gray-800 hover:bg-white/50 rounded-2xl transition-all duration-300">
                了解更多功能
              </Button>
            </Link>
          </div>
        </div>

        {/* 底部装饰 */}
        <div className="text-center pb-6">
          <p className="text-xs text-gray-500">
            基于树莓派5 · 大AI哥数智化工具
          </p>
        </div>
      </div>
    </div>
  );
}
