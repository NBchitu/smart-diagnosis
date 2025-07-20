'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface SmoothNumberProps {
  value: number
  suffix?: string
  className?: string
  decimals?: number
}

export function SmoothNumber({ 
  value, 
  suffix = '',
  className,
  decimals = 0
}: SmoothNumberProps) {
  const [displayValue, setDisplayValue] = useState(value)
  const [isChanging, setIsChanging] = useState(false)

  useEffect(() => {
    if (Math.abs(value - displayValue) < 0.01) return

    setIsChanging(true)
    
    const timer = setTimeout(() => {
      setDisplayValue(value)
      setIsChanging(false)
    }, 150)

    return () => clearTimeout(timer)
  }, [value, displayValue])

  const formatValue = (val: number) => {
    return decimals > 0 ? val.toFixed(decimals) : Math.round(val).toString()
  }

  return (
    <span 
      className={cn(
        "transition-all duration-300 tabular-nums inline-block",
        isChanging && "scale-105 text-blue-600",
        className
      )}
      style={{ minWidth: '60px' }}
    >
      {formatValue(displayValue)}{suffix}
    </span>
  )
} 