import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { CreateEstimateDialog } from "@/components/CreateEstimateDialog";
import { ImportDialog } from "@/components/ImportDialog";

export default function Dashboard() {
  // Mock data for charts
  const costBreakdown = [
    { name: "Direct Costs", value: 450000, color: "#3b82f6" },
    { name: "Indirect Costs", value: 120000, color: "#10b981" },
    { name: "Overhead", value: 80000, color: "#f59e0b" },
    { name: "Profit", value: 65000, color: "#ef4444" },
  ];

  const recentEstimates = [
    { id: 1, name: "Office Building - Phase 1", total: 715000, date: "2024-01-15", status: "In Progress" },
    { id: 2, name: "Residential Complex", total: 1250000, date: "2024-01-10", status: "Completed" },
    { id: 3, name: "Warehouse Renovation", total: 320000, date: "2024-01-05", status: "Draft" },
  ];

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
          <ImportDialog />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Estimates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">+2 from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">Currently in progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$2.8M</div>
            <p className="text-xs text-muted-foreground">Across all estimates</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. OH&P</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18.5%</div>
            <p className="text-xs text-muted-foreground">Overhead & Profit</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Estimates */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Breakdown Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
            <CardDescription>Distribution of costs across categories</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={costBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {costBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Estimates */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Estimates</CardTitle>
            <CardDescription>Your latest estimate projects</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentEstimates.map((estimate) => (
                <div key={estimate.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <h4 className="font-medium">{estimate.name}</h4>
                    <p className="text-sm text-muted-foreground">{estimate.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">${estimate.total.toLocaleString()}</p>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      estimate.status === 'Completed' ? 'bg-green-100 text-green-800' :
                      estimate.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {estimate.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
