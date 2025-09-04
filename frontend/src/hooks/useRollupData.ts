import { useQuery, useQueryClient } from '@tanstack/react-query'

interface RollupData {
  estimate_id: string
  rollup: {
    project_info: {
      name: string
      client: string
      overhead_percent: number
      profit_percent: number
      aace_class: string
    }
    cost_summary: {
      total_cost: number
      total_material: number
      total_labor: number
      total_equipment: number
      total_overhead: number
      total_profit: number
      cost_per_sf: number
    }
    cost_percentages: {
      material_pct: number
      labor_pct: number
      equipment_pct: number
      overhead_pct: number
      profit_pct: number
    }
    rollups: {
      by_phase: Record<string, {
        material: number
        labor: number
        equipment: number
        overhead: number
        profit: number
        subtotal: number
        total: number
        quantity: number
      }>
      by_trade: Record<string, {
        material: number
        labor: number
        equipment: number
        overhead: number
        profit: number
        subtotal: number
        total: number
        quantity: number
      }>
    }
  }
  project_info: {
    name: string
    client: string
    overhead_percent: number
    profit_percent: number
    aace_class: string
  }
}

export function useRollupData(estimateId: string) {
  const queryClient = useQueryClient()

  const {
    data: rollupData,
    isLoading,
    error,
    refetch
  } = useQuery<RollupData>({
    queryKey: ['rollup', estimateId],
    queryFn: async () => {
      const response = await fetch(`/api/estimates/${estimateId}/rollup`)
      if (!response.ok) {
        throw new Error('Failed to fetch rollup data')
      }
      return response.json()
    },
    enabled: !!estimateId,
    refetchInterval: false, // Don't auto-refetch, we'll trigger manually
    staleTime: 0, // Always consider data stale to ensure fresh calculations
  })

  // Function to invalidate and refetch rollup data
  const refreshRollupData = () => {
    queryClient.invalidateQueries({ queryKey: ['rollup', estimateId] })
  }

  // Helper function to get phase data for charts
  const getPhaseChartData = () => {
    if (!rollupData?.rollup?.rollups?.by_phase) return []
    
    return Object.entries(rollupData.rollup.rollups.by_phase).map(([phase, data]) => ({
      name: phase,
      value: data.total,
      color: getPhaseColor(phase)
    }))
  }

  // Helper function to get trade data for charts
  const getTradeChartData = () => {
    if (!rollupData?.rollup?.rollups?.by_trade) return []
    
    return Object.entries(rollupData.rollup.rollups.by_trade).map(([trade, data]) => ({
      trade,
      direct: data.subtotal,
      indirect: data.overhead,
      overhead: data.profit
    }))
  }

  // Helper function to get cost breakdown data
  const getCostBreakdownData = () => {
    if (!rollupData?.rollup?.cost_summary) return []
    
    const { cost_summary } = rollupData.rollup
    return [
      { name: "Direct Costs", value: cost_summary.total_material + cost_summary.total_labor + cost_summary.total_equipment, color: "#3b82f6" },
      { name: "Indirect Costs", value: cost_summary.total_overhead, color: "#10b981" },
      { name: "Overhead", value: cost_summary.total_overhead, color: "#f59e0b" },
      { name: "Profit", value: cost_summary.total_profit, color: "#ef4444" },
    ]
  }

  return {
    rollupData,
    isLoading,
    error,
    refetch,
    refreshRollupData,
    getPhaseChartData,
    getTradeChartData,
    getCostBreakdownData
  }
}

// Helper function to assign colors to phases
function getPhaseColor(phase: string): string {
  const colors = [
    "#3b82f6", // blue
    "#10b981", // green
    "#f59e0b", // yellow
    "#ef4444", // red
    "#8b5cf6", // purple
    "#06b6d4", // cyan
    "#84cc16", // lime
    "#f97316", // orange
    "#ec4899", // pink
    "#6b7280", // gray
  ]
  
  // Simple hash function to get consistent colors for phases
  let hash = 0
  for (let i = 0; i < phase.length; i++) {
    const char = phase.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }
  
  return colors[Math.abs(hash) % colors.length]
}
