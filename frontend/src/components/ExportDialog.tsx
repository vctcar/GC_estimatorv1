"use client"

import { useState } from "react"
import * as XLSX from "exceljs"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Download, FileSpreadsheet, FileText, FileJson, CheckCircle, Loader2 } from "lucide-react"

interface ExportDialogProps {
  trigger?: React.ReactNode
  estimateData: any
  rollupData: any
  onExportComplete?: () => void
}

export function ExportDialog({ trigger, estimateData, rollupData, onExportComplete }: ExportDialogProps) {
  const [open, setOpen] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportFormat, setExportFormat] = useState<string>("xlsx")
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const exportFormats = [
    { value: "xlsx", label: "Excel (.xlsx)", icon: FileSpreadsheet },
    { value: "csv", label: "CSV (.csv)", icon: FileText },
    { value: "json", label: "JSON (.json)", icon: FileJson },
  ]

  const generateExcelFile = async () => {
    const workbook = new XLSX.Workbook()
    
    // Summary sheet
    const summarySheet = workbook.addWorksheet("Summary")
    summarySheet.columns = [
      { header: "Category", key: "category", width: 20 },
      { header: "Value", key: "value", width: 15 },
    ]
    
    // Add summary data
    const summaryData = [
      { category: "Project Name", value: estimateData?.name || "N/A" },
      { category: "Client", value: estimateData?.client || "N/A" },
      { category: "AACE Class", value: estimateData?.aace_class || "N/A" },
      { category: "Status", value: estimateData?.status || "N/A" },
      { category: "Created", value: estimateData?.created || "N/A" },
      { category: "Last Modified", value: estimateData?.lastModified || "N/A" },
      { category: "", value: "" },
      { category: "Direct Costs", value: rollupData?.rollup?.cost_summary?.total_material + rollupData?.rollup?.cost_summary?.total_labor + rollupData?.rollup?.cost_summary?.total_equipment || 0 },
      { category: "Overhead", value: rollupData?.rollup?.cost_summary?.total_overhead || 0 },
      { category: "Profit", value: rollupData?.rollup?.cost_summary?.total_profit || 0 },
      { category: "Total Estimate", value: rollupData?.rollup?.cost_summary?.total_cost || 0 },
    ]
    
    summarySheet.addRows(summaryData)
    
    // Items sheet
    const itemsSheet = workbook.addWorksheet("Line Items")
    itemsSheet.columns = [
      { header: "Phase", key: "phase", width: 15 },
      { header: "Item", key: "item", width: 30 },
      { header: "Unit", key: "unit", width: 10 },
      { header: "Quantity", key: "quantity", width: 12 },
      { header: "Waste %", key: "waste", width: 10 },
      { header: "Unit Cost", key: "unit_cost", width: 12 },
      { header: "Lump Sum", key: "lump_sum", width: 12 },
      { header: "Subtotal", key: "subtotal", width: 12 },
    ]
    
    // Add items data
    if (estimateData?.items) {
      itemsSheet.addRows(estimateData.items)
    }
    
    // Phase summary sheet
    if (rollupData?.rollup?.rollups?.by_phase) {
      const phaseSheet = workbook.addWorksheet("Phase Summary")
      phaseSheet.columns = [
        { header: "Phase", key: "phase", width: 20 },
        { header: "Material", key: "material", width: 15 },
        { header: "Labor", key: "labor", width: 15 },
        { header: "Equipment", key: "equipment", width: 15 },
        { header: "Overhead", key: "overhead", width: 15 },
        { header: "Profit", key: "profit", width: 15 },
        { header: "Total", key: "total", width: 15 },
      ]
      
      const phaseData = Object.entries(rollupData.rollup.rollups.by_phase).map(([phase, data]: [string, any]) => ({
        phase,
        material: data.material || 0,
        labor: data.labor || 0,
        equipment: data.equipment || 0,
        overhead: data.overhead || 0,
        profit: data.profit || 0,
        total: data.total || 0,
      }))
      
      phaseSheet.addRows(phaseData)
    }
    
    return workbook
  }

  const generateCSVContent = () => {
    const lines = []
    
    // Summary section
    lines.push("ESTIMATE SUMMARY")
    lines.push("Project Name," + (estimateData?.name || "N/A"))
    lines.push("Client," + (estimateData?.client || "N/A"))
    lines.push("AACE Class," + (estimateData?.aace_class || "N/A"))
    lines.push("Status," + (estimateData?.status || "N/A"))
    lines.push("Created," + (estimateData?.created || "N/A"))
    lines.push("Last Modified," + (estimateData?.lastModified || "N/A"))
    lines.push("")
    lines.push("Direct Costs," + (rollupData?.rollup?.cost_summary?.total_material + rollupData?.rollup?.cost_summary?.total_labor + rollupData?.rollup?.cost_summary?.total_equipment || 0))
    lines.push("Overhead," + (rollupData?.rollup?.cost_summary?.total_overhead || 0))
    lines.push("Profit," + (rollupData?.rollup?.cost_summary?.total_profit || 0))
    lines.push("Total Estimate," + (rollupData?.rollup?.cost_summary?.total_cost || 0))
    lines.push("")
    
    // Items section
    lines.push("LINE ITEMS")
    lines.push("Phase,Item,Unit,Quantity,Waste %,Unit Cost,Lump Sum,Subtotal")
    
    if (estimateData?.items) {
      estimateData.items.forEach((item: any) => {
        lines.push(`${item.phase},${item.item},${item.unit},${item.quantity},${item.waste},${item.unit_cost},${item.lump_sum},${item.subtotal}`)
      })
    }
    
    return lines.join("\n")
  }

  const handleExport = async () => {
    setExporting(true)
    setError(null)
    setSuccess(null)

    try {
      let blob: Blob
      let filename: string
      const timestamp = new Date().toISOString().split('T')[0]
      const projectName = estimateData?.name?.replace(/[^a-zA-Z0-9]/g, '_') || 'estimate'

      switch (exportFormat) {
        case "xlsx":
          const workbook = await generateExcelFile()
          const buffer = await workbook.xlsx.writeBuffer()
          blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
          filename = `${projectName}_${timestamp}.xlsx`
          break

        case "csv":
          const csvContent = generateCSVContent()
          blob = new Blob([csvContent], { type: 'text/csv' })
          filename = `${projectName}_${timestamp}.csv`
          break

        case "json":
          const jsonData = {
            estimate: estimateData,
            rollup: rollupData,
            exported_at: new Date().toISOString()
          }
          blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' })
          filename = `${projectName}_${timestamp}.json`
          break

        default:
          throw new Error("Unsupported export format")
      }

      // Download the file
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      setSuccess(`Successfully exported estimate as ${exportFormat.toUpperCase()}`)
      onExportComplete?.()
      
      // Close dialog after success
      setTimeout(() => setOpen(false), 2000)
    } catch (error) {
      console.error("Export error:", error)
      setError(`Failed to export: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setExporting(false)
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen)
    if (!newOpen) {
      setError(null)
      setSuccess(null)
      setExporting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Export Estimate</DialogTitle>
          <DialogDescription>
            Choose a format to export your estimate data
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Export Format Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Export Format</label>
            <Select value={exportFormat} onValueChange={setExportFormat}>
              <SelectTrigger>
                <SelectValue placeholder="Select export format" />
              </SelectTrigger>
              <SelectContent>
                {exportFormats.map((format) => {
                  const Icon = format.icon
                  return (
                    <SelectItem key={format.value} value={format.value}>
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        {format.label}
                      </div>
                    </SelectItem>
                  )
                })}
              </SelectContent>
            </Select>
          </div>

          {/* Export Preview */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Export Contents</label>
            <div className="text-sm text-muted-foreground space-y-1">
              <div>• Project summary and metadata</div>
              <div>• All line items with costs</div>
              <div>• Phase and trade breakdowns</div>
              <div>• Cost calculations and totals</div>
            </div>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={exporting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-2"
          >
            {exporting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Export {exportFormat.toUpperCase()}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
