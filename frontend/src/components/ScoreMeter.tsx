import { motion } from 'framer-motion'
import { cn, scoreColor } from '@/lib/utils'

interface ScoreMeterProps {
  score: number // 0-5
  size?: 'sm' | 'md' | 'lg'
  animate?: boolean
  className?: string
}

const SIZES = {
  sm: { r: 20, stroke: 4, fontSize: 'text-xs', wrapper: 'w-12 h-12' },
  md: { r: 32, stroke: 5, fontSize: 'text-sm', wrapper: 'w-20 h-20' },
  lg: { r: 52, stroke: 6, fontSize: 'text-xl', wrapper: 'w-32 h-32' },
}

export function ScoreMeter({ score, size = 'md', animate = true, className }: ScoreMeterProps) {
  const { r, stroke, fontSize, wrapper } = SIZES[size]
  const cx = r + stroke + 2
  const cy = r + stroke + 2
  const svgSize = cx * 2
  const circumference = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(1, score / 5))
  const dash = circumference * pct
  const gap = circumference - dash

  const colorClass = scoreColor(score)

  return (
    <div className={cn('relative flex items-center justify-center', wrapper, className)}>
      <svg width={svgSize} height={svgSize} className="-rotate-90">
        {/* Background ring */}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={stroke} />
        {/* Progress ring */}
        <motion.circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={score >= 4.5 ? '#34d399' : score >= 3.5 ? '#fbbf24' : score >= 2.5 ? '#fb923c' : '#f87171'}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          initial={{ strokeDashoffset: circumference }}
          animate={animate ? { strokeDashoffset: circumference - dash } : {}}
          transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
        />
      </svg>
      <span className={cn('absolute font-display font-bold', fontSize, colorClass)}>
        {score.toFixed(1)}
      </span>
    </div>
  )
}
