"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { CheckCircle, AlertCircle, Loader2, Save } from "lucide-react"

interface SaveEstimateProps {
  estimateId: string
  estimateData: any
  onSaveComplete?: () => void
  trigger?: React.ReactNode
}

export function SaveEstimate({ estimateId, estimateData, onSaveComplete, trigger }: SaveEstimateProps) {
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    setSuccess(null)

    try {
      // Save estimate metadata
      const response = await fetch(`/api/estimates/${estimateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: estimateData.name,
          client: estimateData.client,
          description: estimateData.description,
          overhead_percent: estimateData.overhead_percent,
          profit_percent: estimateData.profit_percent,
          aace_class: estimateData.aace_class,
          status: estimateData.status,
          metadata: estimateData.metadata || {}
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setSuccess("Estimate saved successfully!")
      onSaveComplete?.()
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000)
    } catch (error) {
      console.error("Save error:", error)
      setError(`Failed to save estimate: ${error instanceof Error ? error.message : 'Unknown error'}`)
      
      // Clear error message after 5 seconds
      setTimeout(() => setError(null), 5000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-2">
      {/* Save Button */}
      <div onClick={handleSave}>
        {trigger || (
          <Button 
            disabled={saving}
            className="flex items-center gap-2"
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save
              </>
            )}
          </Button>
        )}
      </div>

      {/* Success/Error Messages */}
      {success && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}
