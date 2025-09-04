"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { HelpCircle, Plus, Loader2, CheckCircle, AlertCircle, Trash2 } from "lucide-react"

// Zod schema for form validation
const itemFormSchema = z.object({
  phase: z.string().min(1, "Phase is required"),
  item: z.string().min(1, "Item description is required").max(200, "Item description must be less than 200 characters"),
  unit: z.string().min(1, "Unit is required"),
  quantity: z.number().min(0, "Quantity must be 0 or higher"),
  waste: z.number().min(0, "Waste must be 0% or higher").max(100, "Waste cannot exceed 100%"),
  unit_cost: z.number().min(0, "Unit cost must be 0 or higher"),
  lump_sum: z.number().min(0, "Lump sum must be 0 or higher"),
})

type ItemFormData = z.infer<typeof itemFormSchema>

interface AddItemDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  estimateId: string
  item?: any // For edit mode
  onItemSaved: () => void
}

export function AddItemDialog({ open, onOpenChange, estimateId, item, onItemSaved }: AddItemDialogProps) {
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [catalogData, setCatalogData] = useState<any>(null)
  const [selectedDivision, setSelectedDivision] = useState<string>("")

  const form = useForm<ItemFormData>({
    resolver: zodResolver(itemFormSchema),
    defaultValues: {
      phase: "",
      item: "",
      unit: "",
      quantity: 0,
      waste: 0,
      unit_cost: 0,
      lump_sum: 0,
    },
  })

  // Load catalog data when dialog opens
  useEffect(() => {
    if (open) {
      loadCatalogData()
    }
  }, [open])

  // Reset form when item prop changes (add/edit mode)
  useEffect(() => {
    if (item) {
      // Edit mode - populate form with item data
      form.reset({
        phase: item.phase || "",
        item: item.item || "",
        unit: item.unit || "",
        quantity: item.quantity || 0,
        waste: item.waste || 0,
        unit_cost: item.unit_cost || 0,
        lump_sum: item.lump_sum || 0,
      })
    } else {
      // Add mode - reset to defaults
      form.reset({
        phase: "",
        item: "",
        unit: "",
        quantity: 0,
        waste: 0,
        unit_cost: 0,
        lump_sum: 0,
      })
    }
    setSelectedDivision("")
  }, [item, form])

  const loadCatalogData = async () => {
    try {
      const response = await fetch("/api/catalogs")
      if (response.ok) {
        const data = await response.json()
        setCatalogData(data)
      }
    } catch (error) {
      console.error("Error loading catalog data:", error)
    }
  }

  const onSubmit = async (data: ItemFormData) => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const url = item 
        ? `/api/estimates/${estimateId}/items/${item.id}`
        : `/api/estimates/${estimateId}/items`
      
      const method = item ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setSuccess(item ? "Item updated successfully!" : "Item added successfully!")
      onItemSaved()
      
      // Close dialog after success
      setTimeout(() => {
        onOpenChange(false)
      }, 1500)
    } catch (error) {
      console.error("Error saving item:", error)
      setError(`Failed to save item: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!item) return

    if (!confirm("Are you sure you want to delete this item?")) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/estimates/${estimateId}/items/${item.id}`, {
        method: "DELETE",
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      setSuccess("Item deleted successfully!")
      onItemSaved()
      
      // Close dialog after success
      setTimeout(() => {
        onOpenChange(false)
      }, 1500)
    } catch (error) {
      console.error("Error deleting item:", error)
      setError(`Failed to delete item: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    onOpenChange(newOpen)
    if (!newOpen) {
      // Reset form and messages when dialog closes
      form.reset()
      setError(null)
      setSuccess(null)
      setLoading(false)
      setSelectedDivision("")
    }
  }

  const handlePhaseChange = (phase: string) => {
    form.setValue("phase", phase)
    setSelectedDivision("")
  }

  const handleDivisionChange = (division: string) => {
    setSelectedDivision(division)
    const masterFormatItem = catalogData?.masterFormatItems?.find((item: any) => item.division === division)
    if (masterFormatItem) {
      form.setValue("item", masterFormatItem.description)
    }
  }

  return (
    <TooltipProvider>
      <Sheet open={open} onOpenChange={handleOpenChange}>
        <SheetContent className="w-[500px] sm:w-[600px] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>{item ? "Edit Item" : "Add New Item"}</SheetTitle>
            <SheetDescription>
              {item ? "Update the line item details below." : "Add a new line item to your estimate."}
            </SheetDescription>
          </SheetHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 mt-6">
              {/* Phase and Item Selection */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-900">Item Information</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="phase"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Phase *</FormLabel>
                        <Select onValueChange={handlePhaseChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select phase" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {catalogData?.phases?.map((phase: string) => (
                              <SelectItem key={phase} value={phase}>
                                {phase}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="unit"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Unit *</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select unit" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {catalogData?.units?.map((unit: string) => (
                              <SelectItem key={unit} value={unit}>
                                {unit}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* MasterFormat Selection */}
                {catalogData?.masterFormatItems && (
                  <div className="space-y-2">
                    <label className="text-sm font-medium">MasterFormat Division (Optional)</label>
                    <Select value={selectedDivision} onValueChange={handleDivisionChange}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select MasterFormat division" />
                      </SelectTrigger>
                      <SelectContent>
                        {catalogData.masterFormatItems.map((item: any) => (
                          <SelectItem key={item.division} value={item.division}>
                            {item.division} - {item.description}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      Select a MasterFormat division to auto-fill the item description
                    </p>
                  </div>
                )}

                <FormField
                  control={form.control}
                  name="item"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Item Description *</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="e.g., Concrete foundation, Electrical wiring, etc." 
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Quantities and Costs */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-900">Quantities and Costs</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="quantity"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-1">
                          Quantity
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Quantity of the item (use 0 for lump sum items)</p>
                            </TooltipContent>
                          </Tooltip>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.01"
                            min="0"
                            className="text-right"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="waste"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-1">
                          Waste (%)
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Waste percentage to add to quantity</p>
                            </TooltipContent>
                          </Tooltip>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.1"
                            min="0"
                            max="100"
                            className="text-right"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="unit_cost"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-1">
                          Unit Cost ($)
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Cost per unit (use 0 for lump sum items)</p>
                            </TooltipContent>
                          </Tooltip>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.01"
                            min="0"
                            className="text-right"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="lump_sum"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-1">
                          Lump Sum ($)
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Fixed cost for the entire item</p>
                            </TooltipContent>
                          </Tooltip>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.01"
                            min="0"
                            className="text-right"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Calculation Preview */}
                <div className="bg-gray-50 p-3 rounded-md">
                  <h5 className="text-sm font-medium mb-2">Calculation Preview</h5>
                  <div className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span>Quantity:</span>
                      <span>{form.watch("quantity") || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Waste ({form.watch("waste") || 0}%):</span>
                      <span>{((form.watch("quantity") || 0) * (form.watch("waste") || 0) / 100).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Quantity:</span>
                      <span>{((form.watch("quantity") || 0) * (1 + (form.watch("waste") || 0) / 100)).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Unit Cost:</span>
                      <span>${(form.watch("unit_cost") || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Lump Sum:</span>
                      <span>${(form.watch("lump_sum") || 0).toFixed(2)}</span>
                    </div>
                    <div className="border-t pt-1 flex justify-between font-medium">
                      <span>Estimated Subtotal:</span>
                      <span>${(((form.watch("quantity") || 0) * (1 + (form.watch("waste") || 0) / 100) * (form.watch("unit_cost") || 0)) + (form.watch("lump_sum") || 0)).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>

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

              <SheetFooter className="flex gap-2">
                {item && (
                  <Button
                    type="button"
                    variant="destructive"
                    onClick={handleDelete}
                    disabled={loading}
                    className="flex items-center gap-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </Button>
                )}
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleOpenChange(false)}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      {item ? "Updating..." : "Adding..."}
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      {item ? "Update Item" : "Add Item"}
                    </>
                  )}
                </Button>
              </SheetFooter>
            </form>
          </Form>
        </SheetContent>
      </Sheet>
    </TooltipProvider>
  )
}
