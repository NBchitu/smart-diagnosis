'use client';

import { cn } from '@/lib/utils';

interface WaveLoadingProps {
  text?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function WaveLoading({ 
  text = "AI正在思考中...", 
  className,
  size = 'md' 
}: WaveLoadingProps) {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const containerClasses = {
    sm: 'gap-1',
    md: 'gap-1.5',
    lg: 'gap-2'
  };

  return (
    <div className={cn("flex flex-col items-center justify-center", className)}>
      {/* 波浪动画 */}
      <div className={cn("flex items-end", containerClasses[size])}>
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className={cn(
              "bg-gradient-to-t from-blue-500 via-purple-500 to-pink-500 rounded-full animate-pulse",
              sizeClasses[size],
              size === 'sm' ? 'w-1' : size === 'md' ? 'w-2' : 'w-3'
            )}
            style={{
              animationDelay: `${i * 0.1}s`,
              animationDuration: '1.4s',
              animationIterationCount: 'infinite',
              animationTimingFunction: 'ease-in-out',
              transform: 'scaleY(0.4)',
              animation: `wave-${size} 1.4s ease-in-out ${i * 0.1}s infinite`
            }}
          />
        ))}
      </div>
      
      {/* 文字提示 */}
      {text && (
        <p className="mt-3 text-sm text-gray-600 animate-pulse">
          {text}
        </p>
      )}
      
      {/* CSS动画定义 */}
      <style jsx>{`
        @keyframes wave-sm {
          0%, 40%, 100% { transform: scaleY(0.4); }
          20% { transform: scaleY(1.2); }
        }
        @keyframes wave-md {
          0%, 40%, 100% { transform: scaleY(0.4); }
          20% { transform: scaleY(1.5); }
        }
        @keyframes wave-lg {
          0%, 40%, 100% { transform: scaleY(0.4); }
          20% { transform: scaleY(1.8); }
        }
      `}</style>
    </div>
  );
}

// 更高级的波浪加载动画
export function AdvancedWaveLoading({ 
  text = "AI正在分析中...", 
  className 
}: WaveLoadingProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-6", className)}>
      {/* 主波浪容器 */}
      <div className="relative w-32 h-16 mb-4">
        {/* 背景波浪 */}
        <div className="absolute inset-0 overflow-hidden rounded-2xl bg-gradient-to-r from-blue-50 to-purple-50 backdrop-blur-sm">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-pink-400/20 animate-pulse" />
        </div>
        
        {/* 动态波浪 */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex items-end gap-1">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="w-1.5 bg-gradient-to-t from-blue-500 via-purple-500 to-pink-500 rounded-full"
                style={{
                  height: '8px',
                  animationDelay: `${i * 0.1}s`,
                  animation: `advancedWave 1.6s ease-in-out infinite`
                }}
              />
            ))}
          </div>
        </div>
        
        {/* 光晕效果 */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl blur-sm animate-pulse" />
      </div>
      
      {/* 文字提示 */}
      <div className="text-center">
        <p className="text-sm font-medium text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 animate-pulse">
          {text}
        </p>
        <div className="flex justify-center mt-2 space-x-1">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="w-1 h-1 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>
      
      {/* CSS动画定义 */}
      <style jsx>{`
        @keyframes advancedWave {
          0%, 40%, 100% { 
            transform: scaleY(0.4);
            opacity: 0.7;
          }
          20% { 
            transform: scaleY(2.5);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

// 科技感波浪动画
export function TechWaveLoading({ 
  text = "AI正在处理中...", 
  className 
}: WaveLoadingProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-8", className)}>
      {/* 科技感容器 */}
      <div className="relative w-40 h-20 mb-6">
        {/* 外层光环 */}
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-purple-500/20 animate-pulse" />
        <div className="absolute inset-1 rounded-3xl bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 backdrop-blur-sm" />
        
        {/* 波浪网格 */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="grid grid-cols-12 gap-0.5 h-8">
            {[...Array(60)].map((_, i) => {
              const row = Math.floor(i / 12);
              const col = i % 12;
              return (
                <div
                  key={i}
                  className="w-0.5 bg-gradient-to-t from-cyan-400 via-blue-500 to-purple-600 rounded-full"
                  style={{
                    height: '2px',
                    animationDelay: `${(col * 0.05) + (row * 0.1)}s`,
                    animation: `techWave 2s ease-in-out infinite`
                  }}
                />
              );
            })}
          </div>
        </div>
        
        {/* 中心光点 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="w-2 h-2 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full animate-ping" />
          <div className="absolute inset-0 w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-pulse" />
        </div>
      </div>
      
      {/* 科技感文字 */}
      <div className="text-center space-y-2">
        <p className="text-base font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600">
          {text}
        </p>
        <div className="flex justify-center space-x-2">
          {['●', '●', '●'].map((dot, i) => (
            <span
              key={i}
              className="text-blue-400 animate-bounce text-xs"
              style={{ animationDelay: `${i * 0.3}s` }}
            >
              {dot}
            </span>
          ))}
        </div>
      </div>
      
      {/* CSS动画定义 */}
      <style jsx>{`
        @keyframes techWave {
          0%, 60%, 100% { 
            transform: scaleY(0.3);
            opacity: 0.4;
          }
          30% { 
            transform: scaleY(3);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}
