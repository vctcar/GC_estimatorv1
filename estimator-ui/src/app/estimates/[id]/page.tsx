"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
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
  const [selectedItem, setSelectedItem] = useState<typeof qtoItems[0] | null>(null);

  const columns: ColumnDef<typeof qtoItems[0]>[] = [
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
        </div>
      ),
    },
  ];

  const table = useReactTable({
    data: qtoItems,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
  });

  const totalDirectCost = qtoItems.reduce((sum, item) => sum + item.subtotal, 0);
  const overhead = totalDirectCost * 0.15; // 15% overhead
  const profit = (totalDirectCost + overhead) * 0.10; // 10% profit
  const totalEstimate = totalDirectCost + overhead + profit;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Office Building - Phase 1</h1>
          <p className="text-muted-foreground">Estimate ID: {params.id}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">Export</Button>
          <Button>Save</Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Direct Costs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${totalDirectCost.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overhead (15%)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${overhead.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profit (10%)</CardTitle>
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
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${totalEstimate.toLocaleString()}
            </div>
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
                <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                  <SheetTrigger asChild>
                    <Button>+ Add Item</Button>
                  </SheetTrigger>
                  <SheetContent className="w-[400px]">
                    <SheetHeader>
                      <SheetTitle>
                        {selectedItem ? "Edit Item" : "Add New Item"}
                      </SheetTitle>
                    </SheetHeader>
                    <div className="mt-6">
                      <p className="text-muted-foreground">
                        Item form will be implemented here with React Hook Form + Zod validation.
                      </p>
                    </div>
                  </SheetContent>
                </Sheet>
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
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={phaseData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {phaseData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Phase Summary Table</CardTitle>
                <CardDescription>Detailed phase breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Phase</TableHead>
                      <TableHead className="text-right">Direct Cost</TableHead>
                      <TableHead className="text-right">Percentage</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {phaseData.map((phase) => (
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
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={tradeData}>
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
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-medium">Direct Costs</h4>
                    <div className="space-y-1">
                      {phaseData.map((phase) => (
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
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
