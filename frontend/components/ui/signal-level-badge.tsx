'use client'

import { Badge } from './badge'
import { cn } from '@/lib/utils'

interface SignalLevelBadgeProps {
  signalStrength: number
  className?: string
}

export function SignalLevelBadge({ signalStrength, className }: SignalLevelBadgeProps) {
  const getSignalConfig = (strength: number) => {
    if (strength >= -30) {
      return {
        level: "极强",
        bgColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
        darkBgColor: "dark:bg-emerald-900/20 dark:text-emerald-300 dark:border-emerald-800"
      }
    }
    if (strength >= -50) {
      return {
        level: "强",
        bgColor: "bg-green-100 text-green-800 border-green-200",
        darkBgColor: "dark:bg-green-900/20 dark:text-green-300 dark:border-green-800"
      }
    }
    if (strength >= -70) {
      return {
        level: "中等",
        bgColor: "bg-yellow-100 text-yellow-800 border-yellow-200",
        darkBgColor: "dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800"
      }
    }
    if (strength >= -80) {
      return {
        level: "弱",
        bgColor: "bg-orange-100 text-orange-800 border-orange-200",
        darkBgColor: "dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800"
      }
    }
    return {
      level: "极弱",
      bgColor: "bg-red-100 text-red-800 border-red-200",
      darkBgColor: "dark:bg-red-900/20 dark:text-red-300 dark:border-red-800"
    }
  }

  const config = getSignalConfig(signalStrength)

  return (
    <Badge 
      variant="outline"
      className={cn(
        "font-medium min-w-[48px] justify-center transition-all duration-300",
        config.bgColor,
        config.darkBgColor,
        className
      )}
    >
      {config.level}
    </Badge>
  )
} 