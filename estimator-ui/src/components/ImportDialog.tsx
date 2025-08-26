"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import * as XLSX from "exceljs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle, Loader2 } from "lucide-react"

interface ImportedItem {
  id: string
  phase: string
  item: string
  unit: string
  quantity: number
  waste: number
  unit_cost: number
  lump_sum: number
  subtotal: number
}

interface ImportDialogProps {
  trigger?: React.ReactNode
  estimateId?: string
  onImportComplete?: () => void
}

export function ImportDialog({ trigger, estimateId, onImportComplete }: ImportDialogProps) {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [importing, setImporting] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [parsedItems, setParsedItems] = useState<ImportedItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [targetEstimateId, setTargetEstimateId] = useState<string>(estimateId || "")
  const [estimates, setEstimates] = useState<Array<{ id: string; name: string }>>([])

  // Load estimates for target selection
  const loadEstimates = async () => {
    try {
      const response = await fetch("/api/estimates")
      if (response.ok) {
        const data = await response.json()
        setEstimates(data.estimates || [])
      }
    } catch (error) {
      console.error("Error loading estimates:", error)
    }
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    const validExtensions = ['.xlsx', '.xls', '.csv']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!validExtensions.includes(fileExtension)) {
      setError("Please select a valid Excel (.xlsx, .xls) or CSV (.csv) file")
      return
    }

    setSelectedFile(file)
    setError(null)
    setSuccess(null)
    setParsedItems([])
    setLoading(true)

    try {
      // Parse the file
      const items = await parseFile(file)
      setParsedItems(items)
      setSuccess(`Successfully parsed ${items.length} items from ${file.name}`)
    } catch (error) {
      console.error("Error parsing file:", error)
      setError(`Failed to parse file: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const parseFile = async (file: File): Promise<ImportedItem[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = async (e) => {
        try {
          const data = e.target?.result
          if (!data) {
            reject(new Error("Failed to read file"))
            return
          }

          const workbook = new XLSX.Workbook()
          
          if (file.name.toLowerCase().endsWith('.csv')) {
            // Handle CSV
            const csvText = data as string
            const worksheet = workbook.addWorksheet('Sheet1')
            
            // Parse CSV manually
            const lines = csvText.split('\n')
            const headers = lines[0]?.split(',').map(h => h.trim()) || []
            
            for (let i = 1; i < lines.length; i++) {
              if (lines[i].trim()) {
                const values = lines[i].split(',').map(v => v.trim())
                const row: any = {}
                headers.forEach((header, index) => {
                  row[header] = values[index] || ''
                })
                worksheet.addRow(row)
              }
            }
          } else {
            // Handle Excel
            await workbook.xlsx.load(data as ArrayBuffer)
          }

          const worksheet = workbook.getWorksheet(1)
          if (!worksheet) {
            reject(new Error("No worksheet found in file"))
            return
          }

          const items: ImportedItem[] = []
          const headers = worksheet.getRow(1).values as string[]
          
          // Find column indices
          const phaseIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('phase') || h?.toLowerCase().includes('trade')
          )
          const itemIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('item') || h?.toLowerCase().includes('description')
          )
          const unitIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('unit') || h?.toLowerCase().includes('uom')
          )
          const quantityIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('quantity') || h?.toLowerCase().includes('qty')
          )
          const wasteIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('waste') || h?.toLowerCase().includes('overage')
          )
          const unitCostIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('unit') && h?.toLowerCase().includes('cost')
          )
          const lumpSumIndex = headers.findIndex(h => 
            h?.toLowerCase().includes('lump') || h?.toLowerCase().includes('fixed')
          )

          // Process rows (skip header)
          for (let i = 2; i <= worksheet.rowCount; i++) {
            const row = worksheet.getRow(i)
            const values = row.values as any[]
            
            if (!values || values.every(v => !v)) continue // Skip empty rows

            const item: ImportedItem = {
              id: `imported-${i}`,
              phase: values[phaseIndex] || '',
              item: values[itemIndex] || '',
              unit: values[unitIndex] || '',
              quantity: parseFloat(values[quantityIndex]) || 0,
              waste: parseFloat(values[wasteIndex]) || 0,
              unit_cost: parseFloat(values[unitCostIndex]) || 0,
              lump_sum: parseFloat(values[lumpSumIndex]) || 0,
              subtotal: 0 // Will be calculated
            }

            // Calculate subtotal
            const totalQuantity = item.quantity * (1 + item.waste / 100)
            item.subtotal = (item.unit_cost * totalQuantity) + item.lump_sum

            items.push(item)
          }

          resolve(items)
        } catch (error) {
          reject(error)
        }
      }

      reader.onerror = () => reject(new Error("Failed to read file"))

      if (file.name.toLowerCase().endsWith('.csv')) {
        reader.readAsText(file)
      } else {
        reader.readAsArrayBuffer(file)
      }
    })
  }

  const handleImport = async () => {
    if (!parsedItems.length) return

    setImporting(true)
    setError(null)

    try {
      if (targetEstimateId) {
        // Import to specific estimate
        const promises = parsedItems.map(item => 
          fetch(`/api/estimates/${targetEstimateId}/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          })
        )

        const results = await Promise.all(promises)
        const failed = results.filter(r => !r.ok)
        
        if (failed.length > 0) {
          throw new Error(`${failed.length} items failed to import`)
        }

        setSuccess(`Successfully imported ${parsedItems.length} items to estimate`)
        onImportComplete?.()
        
        // Close dialog and redirect to estimate
        setTimeout(() => {
          setOpen(false)
          router.push(`/estimates/${targetEstimateId}`)
        }, 2000)
      } else {
        // Use the backend import endpoint
        const formData = new FormData()
        formData.append('file', selectedFile!)

        const response = await fetch('/api/estimates/import', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }

        const result = await response.json()
        setSuccess(`Successfully imported ${result.total_items} items using backend parser`)
        
        // Close dialog after success
        setTimeout(() => setOpen(false), 2000)
      }
    } catch (error) {
      console.error("Error importing items:", error)
      setError(`Failed to import items: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setImporting(false)
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen)
    if (newOpen) {
      loadEstimates()
    } else {
      // Reset state
      setSelectedFile(null)
      setParsedItems([])
      setError(null)
      setSuccess(null)
      setLoading(false)
      setImporting(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" className="flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Import Excel/CSV
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import Excel/CSV File</DialogTitle>
          <DialogDescription>
            Upload an Excel or CSV file to import line items. The file should contain columns for Phase, Item, Unit, Quantity, etc.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5" />
                File Upload
              </CardTitle>
              <CardDescription>
                Select an Excel (.xlsx, .xls) or CSV (.csv) file to import.{" "}
                <a 
                  href="/sample-import-template.csv" 
                  download
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  Download sample template
                </a>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileSelect}
                  disabled={loading}
                />
                
                {loading && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Parsing file...
                  </div>
                )}

                {selectedFile && (
                  <div className="text-sm text-muted-foreground">
                    Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Error/Success Messages */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Target Estimate Selection */}
          {parsedItems.length > 0 && !estimateId && (
            <Card>
              <CardHeader>
                <CardTitle>Import Target</CardTitle>
                <CardDescription>
                  Select which estimate to import the items into
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Select value={targetEstimateId} onValueChange={setTargetEstimateId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select an estimate" />
                  </SelectTrigger>
                  <SelectContent>
                    {estimates.map((estimate) => (
                      <SelectItem key={estimate.id} value={estimate.id}>
                        {estimate.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          )}

          {/* Preview Table */}
          {parsedItems.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Preview ({parsedItems.length} items)</CardTitle>
                <CardDescription>
                  Review the parsed items before importing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-96 overflow-y-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Phase</TableHead>
                        <TableHead>Item</TableHead>
                        <TableHead>Unit</TableHead>
                        <TableHead className="text-right">Quantity</TableHead>
                        <TableHead className="text-right">Waste %</TableHead>
                        <TableHead className="text-right">Unit Cost</TableHead>
                        <TableHead className="text-right">Lump Sum</TableHead>
                        <TableHead className="text-right">Subtotal</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {parsedItems.map((item, index) => (
                        <TableRow key={item.id}>
                          <TableCell className="font-medium">{item.phase}</TableCell>
                          <TableCell>{item.item}</TableCell>
                          <TableCell>{item.unit}</TableCell>
                          <TableCell className="text-right">{item.quantity.toLocaleString()}</TableCell>
                          <TableCell className="text-right">{item.waste}%</TableCell>
                          <TableCell className="text-right">
                            ${item.unit_cost.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-right">
                            ${item.lump_sum.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            ${item.subtotal.toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={importing}
          >
            Cancel
          </Button>
          <Button
            onClick={handleImport}
            disabled={!parsedItems.length || !targetEstimateId || importing}
            className="flex items-center gap-2"
          >
            {importing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Importing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Import {parsedItems.length} Items
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
