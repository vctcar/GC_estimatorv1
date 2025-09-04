import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateEstimateDialog } from "@/components/CreateEstimateDialog";

export default function Dashboard() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">GC Estimator Dashboard</h1>
          <p className="text-muted-foreground">Manage and track your construction estimates</p>
        </div>
        <div className="flex space-x-2">
          <CreateEstimateDialog />
          <Link href="/estimates">
            <Button variant="outline">View All Estimates</Button>
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>📊</span>
              <span>Create New Estimate</span>
            </CardTitle>
            <CardDescription>Start a new construction cost estimate</CardDescription>
          </CardHeader>
          <CardContent>
            <CreateEstimateDialog />
          </CardContent>
        </Card>

        <Link href="/estimates">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <span>📋</span>
                <span>View Estimates</span>
              </CardTitle>
              <CardDescription>Browse and manage existing estimates</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                Go to Estimates
              </Button>
            </CardContent>
          </Card>
        </Link>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>📤</span>
              <span>Import QTO</span>
            </CardTitle>
            <CardDescription>Upload Excel/CSV files to create estimates</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/estimates">
              <Button variant="outline" className="w-full">
                Import File
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>Quick guide to using GC Estimator</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">1</span>
            <div>
              <h4 className="font-medium">Create an Estimate</h4>
              <p className="text-sm text-muted-foreground">Start by creating a new estimate or importing a QTO file</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">2</span>
            <div>
              <h4 className="font-medium">Add Line Items</h4>
              <p className="text-sm text-muted-foreground">Add construction items with quantities, costs, and phases</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">3</span>
            <div>
              <h4 className="font-medium">Review Costs</h4>
              <p className="text-sm text-muted-foreground">View cost breakdowns, rollups, and generate reports</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
