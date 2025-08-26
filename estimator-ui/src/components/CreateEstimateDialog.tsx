"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { HelpCircle, Plus, Loader2, CheckCircle, AlertCircle } from "lucide-react"

// Zod schema for form validation
const createEstimateSchema = z.object({
  name: z.string().min(1, "Project name is required").max(100, "Project name must be less than 100 characters"),
  client: z.string().min(1, "Client name is required").max(100, "Client name must be less than 100 characters"),
  description: z.string().optional(),
  aace_class: z.string().min(1, "AACE class is required"),
  overhead_percent: z.number().min(0, "Overhead must be 0% or higher").max(100, "Overhead cannot exceed 100%"),
  profit_percent: z.number().min(0, "Profit must be 0% or higher").max(100, "Profit cannot exceed 100%"),
})

type CreateEstimateFormData = z.infer<typeof createEstimateSchema>

const aaceClasses = [
  { value: "Class 1", label: "Class 1 - Order of Magnitude (±50%)" },
  { value: "Class 2", label: "Class 2 - Feasibility (±30%)" },
  { value: "Class 3", label: "Class 3 - Budget (±20%)" },
  { value: "Class 4", label: "Class 4 - Definitive (±10%)" },
  { value: "Class 5", label: "Class 5 - Detailed (±5%)" },
]

interface CreateEstimateDialogProps {
  trigger?: React.ReactNode
}

export function CreateEstimateDialog({ trigger }: CreateEstimateDialogProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const form = useForm<CreateEstimateFormData>({
    resolver: zodResolver(createEstimateSchema),
    defaultValues: {
      name: "",
      client: "",
      description: "",
      aace_class: "Class 3",
      overhead_percent: 15,
      profit_percent: 10,
    },
  })

  const onSubmit = async (data: CreateEstimateFormData) => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await fetch("/api/estimates", {
        method: "POST",
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
      setSuccess("Estimate created successfully!")
      
      // Redirect to the new estimate after a brief delay
      setTimeout(() => {
        router.push(`/estimates/${result.estimate.id}`)
      }, 1500)
    } catch (error) {
      console.error("Error creating estimate:", error)
      setError(`Failed to create estimate: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen)
    if (!newOpen) {
      // Reset form and messages when dialog closes
      form.reset()
      setError(null)
      setSuccess(null)
      setLoading(false)
    }
  }

  return (
    <TooltipProvider>
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogTrigger asChild>
          {trigger || (
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              New Estimate
            </Button>
          )}
        </DialogTrigger>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Estimate</DialogTitle>
            <DialogDescription>
              Enter the basic information for your new construction estimate
            </DialogDescription>
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Project Information */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-900">Project Information</h4>
                
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Project Name *</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., Office Building - Phase 1" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="client"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Client *</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., ABC Construction Company" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Description</FormLabel>
                      <FormControl>
                        <Input placeholder="Brief project description (optional)" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Estimate Settings */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-900">Estimate Settings</h4>
                
                <FormField
                  control={form.control}
                  name="aace_class"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>AACE Class *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select AACE class" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {aaceClasses.map((aaceClass) => (
                            <SelectItem key={aaceClass.value} value={aaceClass.value}>
                              {aaceClass.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormDescription>
                        Determines the accuracy level and methodology for cost estimation
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="overhead_percent"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-1">
                          Overhead (%)
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>General overhead costs as a percentage of direct costs</p>
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

                  <FormField
                    control={form.control}
                    name="profit_percent"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center gap-1">
                          Profit (%)
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Profit margin as a percentage of total costs</p>
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

              <DialogFooter>
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
                      Creating...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      Create Estimate
                    </>
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </TooltipProvider>
  )
}
