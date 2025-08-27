"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AddItemDialog } from "@/components/AddItemDialog";
import { ImportDialog } from "@/components/ImportDialog";
import { ExportDialog } from "@/components/ExportDialog";
import { SaveEstimate } from "@/components/SaveEstimate";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
} from "@tanstack/react-table";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { Upload, Loader2 } from "lucide-react";
import { useRollupData } from "@/hooks/useRollupData";

// Mock data for QTO items
const qtoItems = [
  {
    id: 1,
    phase: "Site Work",
    item: "Excavation",
    unit: "CY",
    quantity: 1500,
    waste: 10,
    unitCost: 25.50,
    lumpSum: 0,
    subtotal: 42187.50,
  },
  {
    id: 2,
    phase: "Site Work",
    item: "Backfill",
    unit: "CY",
    quantity: 1200,
    waste: 5,
    unitCost: 18.75,
    lumpSum: 0,
    subtotal: 23625.00,
  },
  {
    id: 3,
    phase: "Concrete",
    item: "Foundation",
    unit: "CY",
    quantity: 800,
    waste: 8,
    unitCost: 450.00,
    lumpSum: 0,
    subtotal: 388800.00,
  },
  {
    id: 4,
    phase: "Concrete",
    item: "Slab on Grade",
    unit: "SF",
    quantity: 5000,
    waste: 3,
    unitCost: 12.50,
    lumpSum: 0,
    subtotal: 64375.00,
  },
  {
    id: 5,
    phase: "Masonry",
    item: "CMU Walls",
    unit: "SF",
    quantity: 3000,
    waste: 5,
    unitCost: 28.00,
    lumpSum: 0,
    subtotal: 88200.00,
  },
];

// Mock data for charts
const phaseData = [
  { name: "Site Work", value: 65812.50, color: "#3b82f6" },
  { name: "Concrete", value: 453175.00, color: "#10b981" },
  { name: "Masonry", value: 88200.00, color: "#f59e0b" },
  { name: "Electrical", value: 125000.00, color: "#ef4444" },
  { name: "Plumbing", value: 95000.00, color: "#8b5cf6" },
];

const tradeData = [
  { trade: "Site Work", direct: 65812.50, indirect: 13162.50, overhead: 7897.50 },
  { trade: "Concrete", direct: 453175.00, indirect: 90635.00, overhead: 54381.00 },
  { trade: "Masonry", direct: 88200.00, indirect: 17640.00, overhead: 10584.00 },
  { trade: "Electrical", direct: 125000.00, indirect: 25000.00, overhead: 15000.00 },
  { trade: "Plumbing", direct: 95000.00, indirect: 19000.00, overhead: 11400.00 },
];

export default function EstimateWorkspace({ params }: { params: { id: string } }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [estimateData, setEstimateData] = useState<any>(null);

  // Use rollup data hook
  const {
    rollupData,
    isLoading: rollupLoading,
    error: rollupError,
    refreshRollupData,
    getPhaseChartData,
    getTradeChartData,
    getCostBreakdownData
  } = useRollupData(params.id);

  // Load estimate data
  useEffect(() => {
    const loadEstimate = async () => {
      try {
        const response = await fetch(`/api/estimates/${params.id}`);
        if (response.ok) {
          const data = await response.json();
          setEstimateData(data.estimate);
          setItems(data.estimate.items || []);
        }
      } catch (error) {
        console.error("Error loading estimate:", error);
      } finally {
        setLoading(false);
      }
    };

    loadEstimate();
  }, [params.id]);

  const refreshItems = () => {
    // Reload items after adding/editing/deleting
    const loadEstimate = async () => {
      try {
        const response = await fetch(`/api/estimates/${params.id}`);
        if (response.ok) {
          const data = await response.json();
          setItems(data.estimate.items || []);
        }
      } catch (error) {
        console.error("Error loading estimate:", error);
      }
    };

    loadEstimate();
    // Also refresh rollup data to update totals and charts
    refreshRollupData();
  };

  const columns: ColumnDef<any>[] = [
    {
      accessorKey: "phase",
      header: "Phase",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("phase")}</div>
      ),
    },
    {
      accessorKey: "item",
      header: "Item",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("item")}</div>
      ),
    },
    {
      accessorKey: "unit",
      header: "Unit",
      cell: ({ row }) => (
        <div className="text-center">{row.getValue("unit")}</div>
      ),
    },
    {
      accessorKey: "quantity",
      header: "Quantity",
      cell: ({ row }) => {
        const quantity = parseFloat(row.getValue("quantity"));
        return <div className="text-right">{quantity.toLocaleString()}</div>;
      },
    },
    {
      accessorKey: "waste",
      header: "Waste %",
      cell: ({ row }) => {
        const waste = parseFloat(row.getValue("waste"));
        return <div className="text-right">{waste}%</div>;
      },
    },
    {
      accessorKey: "unitCost",
      header: "Unit Cost",
      cell: ({ row }) => {
        const cost = parseFloat(row.getValue("unitCost"));
        const formatted = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
        }).format(cost);
        return <div className="text-right">{formatted}</div>;
      },
    },
    {
      accessorKey: "lumpSum",
      header: "Lump Sum",
      cell: ({ row }) => {
        const lumpSum = parseFloat(row.getValue("lumpSum"));
        const formatted = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
        }).format(lumpSum);
        return <div className="text-right">{formatted}</div>;
      },
    },
    {
      accessorKey: "subtotal",
      header: "Subtotal",
      cell: ({ row }) => {
        const subtotal = parseFloat(row.getValue("subtotal"));
        const formatted = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
        }).format(subtotal);
        return <div className="text-right font-medium">{formatted}</div>;
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSelectedItem(row.original);
              setIsSheetOpen(true);
            }}
          >
            Edit
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={async () => {
              if (confirm("Are you sure you want to delete this item?")) {
                try {
                  const response = await fetch(`/api/estimates/${params.id}/items/${row.original.id}`, {
                    method: "DELETE",
                  });
                  if (response.ok) {
                    refreshItems();
                  } else {
                    alert("Failed to delete item");
                  }
                } catch (error) {
                  console.error("Error deleting item:", error);
                  alert("Failed to delete item");
                }
              }
            }}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  const table = useReactTable({
    data: items,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
  });

  // Use rollup data for totals, fallback to local calculations if not available
  const rollupSummary = rollupData?.rollup?.cost_summary;
  const totalDirectCost = rollupSummary ? 
    (rollupSummary.total_material || 0) + (rollupSummary.total_labor || 0) + (rollupSummary.total_equipment || 0) :
    items.reduce((sum, item) => sum + (item.subtotal || 0), 0);
  
  const overhead = rollupSummary?.total_overhead || (totalDirectCost * 0.15);
  const profit = rollupSummary?.total_profit || ((totalDirectCost + overhead) * 0.10);
  const totalEstimate = rollupSummary?.total_cost || (totalDirectCost + overhead + profit);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Office Building - Phase 1</h1>
          <p className="text-muted-foreground">Estimate ID: {params.id}</p>
        </div>
        <div className="flex space-x-2">
          <ExportDialog 
            estimateData={estimateData}
            rollupData={rollupData}
          />
          <SaveEstimate 
            estimateId={params.id}
            estimateData={estimateData}
            onSaveComplete={refreshItems}
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Direct Costs</CardTitle>
            {rollupLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${totalDirectCost.toLocaleString()}
            </div>
            {rollupData?.rollup?.cost_percentages && (
              <p className="text-xs text-muted-foreground">
                Material: {rollupData.rollup.cost_percentages.material_pct.toFixed(1)}% | 
                Labor: {rollupData.rollup.cost_percentages.labor_pct.toFixed(1)}%
              </p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Overhead ({rollupData?.project_info?.overhead_percent || 15}%)
            </CardTitle>
            {rollupLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${overhead.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Profit ({rollupData?.project_info?.profit_percent || 10}%)
            </CardTitle>
            {rollupLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${profit.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Estimate</CardTitle>
            {rollupLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${totalEstimate.toLocaleString()}
            </div>
            {rollupData?.rollup?.cost_summary?.cost_per_sf && (
              <p className="text-xs text-muted-foreground">
                ${rollupData.rollup.cost_summary.cost_per_sf.toFixed(2)}/SF
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Content with Tabs */}
      <Tabs defaultValue="items" className="space-y-4">
        <TabsList>
          <TabsTrigger value="items">Items</TabsTrigger>
          <TabsTrigger value="phase-summary">Phase Summary</TabsTrigger>
          <TabsTrigger value="trade-summary">Trade Summary</TabsTrigger>
          <TabsTrigger value="cost-breakdown">Cost Breakdown</TabsTrigger>
        </TabsList>

        <TabsContent value="items" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Quantity Takeoff</CardTitle>
                  <CardDescription>Detailed line items for the estimate</CardDescription>
                </div>
                <div className="flex space-x-2">
                  <Button onClick={() => setIsSheetOpen(true)}>+ Add Item</Button>
                  <ImportDialog 
                    estimateId={params.id}
                    onImportComplete={refreshItems}
                    trigger={
                      <Button variant="outline" className="flex items-center gap-2">
                        <Upload className="h-4 w-4" />
                        Import
                      </Button>
                    }
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    {table.getHeaderGroups().map((headerGroup) => (
                      <TableRow key={headerGroup.id}>
                        {headerGroup.headers.map((header) => {
                          return (
                            <TableHead key={header.id}>
                              {header.isPlaceholder
                                ? null
                                : flexRender(
                                    header.column.columnDef.header,
                                    header.getContext()
                                  )}
                            </TableHead>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableHeader>
                  <TableBody>
                    {table.getRowModel().rows?.length ? (
                      table.getRowModel().rows.map((row) => (
                        <TableRow
                          key={row.id}
                          data-state={row.getIsSelected() && "selected"}
                        >
                          {row.getVisibleCells().map((cell) => (
                            <TableCell key={cell.id}>
                              {flexRender(
                                cell.column.columnDef.cell,
                                cell.getContext()
                              )}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell
                          colSpan={columns.length}
                          className="h-24 text-center"
                        >
                          No items found.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="phase-summary" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Phase Distribution</CardTitle>
                <CardDescription>Cost breakdown by construction phase</CardDescription>
              </CardHeader>
              <CardContent>
                {rollupLoading ? (
                  <div className="flex items-center justify-center h-[300px]">
                    <Loader2 className="h-8 w-8 animate-spin" />
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={getPhaseChartData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${((percent as number || 0) * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getPhaseChartData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Phase Summary Table</CardTitle>
                <CardDescription>Detailed phase breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                {rollupLoading ? (
                  <div className="flex items-center justify-center h-[200px]">
                    <Loader2 className="h-6 w-6 animate-spin" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Phase</TableHead>
                        <TableHead className="text-right">Direct Cost</TableHead>
                        <TableHead className="text-right">Percentage</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {getPhaseChartData().map((phase) => (
                        <TableRow key={phase.name}>
                          <TableCell className="font-medium">{phase.name}</TableCell>
                          <TableCell className="text-right">
                            ${phase.value.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-right">
                            {((phase.value / totalDirectCost) * 100).toFixed(1)}%
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trade-summary" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Trade Summary</CardTitle>
              <CardDescription>Cost breakdown by trade with direct, indirect, and overhead costs</CardDescription>
            </CardHeader>
            <CardContent>
              {rollupLoading ? (
                <div className="flex items-center justify-center h-[400px]">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={getTradeChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="trade" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="direct" fill="#3b82f6" name="Direct Cost" />
                    <Bar dataKey="indirect" fill="#10b981" name="Indirect Cost" />
                    <Bar dataKey="overhead" fill="#f59e0b" name="Overhead" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cost-breakdown" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown</CardTitle>
              <CardDescription>Complete cost analysis and summary</CardDescription>
            </CardHeader>
            <CardContent>
              {rollupLoading ? (
                <div className="flex items-center justify-center h-[400px]">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <h4 className="font-medium">Direct Costs</h4>
                      <div className="space-y-1">
                        {getPhaseChartData().map((phase) => (
                          <div key={phase.name} className="flex justify-between text-sm">
                            <span>{phase.name}</span>
                            <span>${phase.value.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                      <div className="border-t pt-2 font-medium">
                        <div className="flex justify-between">
                          <span>Total Direct</span>
                          <span>${totalDirectCost.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  <div className="space-y-2">
                    <h4 className="font-medium">Indirect Costs</h4>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>Overhead (15%)</span>
                        <span>${overhead.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Profit (10%)</span>
                        <span>${profit.toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="border-t pt-2 font-medium">
                      <div className="flex justify-between">
                        <span>Total Estimate</span>
                        <span>${totalEstimate.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add/Edit Item Dialog */}
      <AddItemDialog
        open={isSheetOpen}
        onOpenChange={setIsSheetOpen}
        estimateId={params.id}
        item={selectedItem}
        onItemSaved={refreshItems}
      />
    </div>
  );
}
