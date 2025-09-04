"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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

// Mock data for estimates
const estimates = [
  {
    id: 1,
    name: "Office Building - Phase 1",
    client: "ABC Corp",
    total: 715000,
    status: "In Progress",
    created: "2024-01-15",
    lastModified: "2024-01-20",
  },
  {
    id: 2,
    name: "Residential Complex",
    client: "XYZ Development",
    total: 1250000,
    status: "Completed",
    created: "2024-01-10",
    lastModified: "2024-01-18",
  },
  {
    id: 3,
    name: "Warehouse Renovation",
    client: "Industrial Co",
    total: 320000,
    status: "Draft",
    created: "2024-01-05",
    lastModified: "2024-01-12",
  },
  {
    id: 4,
    name: "Shopping Center",
    client: "Retail Partners",
    total: 890000,
    status: "In Progress",
    created: "2024-01-08",
    lastModified: "2024-01-19",
  },
];

export default function EstimatesList() {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const columns: ColumnDef<typeof estimates[0]>[] = [
    {
      accessorKey: "name",
      header: "Estimate Name",
      cell: ({ row }) => (
        <div className="font-medium">
          <a href={`/estimates/${row.original.id}`} className="text-blue-600 hover:underline">
            {row.getValue("name")}
          </a>
        </div>
      ),
    },
    {
      accessorKey: "client",
      header: "Client",
    },
    {
      accessorKey: "total",
      header: "Total",
      cell: ({ row }) => {
        const amount = parseFloat(row.getValue("total"));
        const formatted = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
        }).format(amount);
        return <div className="font-medium">{formatted}</div>;
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as string;
        return (
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              status === "Completed"
                ? "bg-green-100 text-green-800"
                : status === "In Progress"
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {status}
          </span>
        );
      },
    },
    {
      accessorKey: "created",
      header: "Created",
      cell: ({ row }) => {
        return <div className="text-sm text-muted-foreground">{row.getValue("created")}</div>;
      },
    },
    {
      accessorKey: "lastModified",
      header: "Last Modified",
      cell: ({ row }) => {
        return <div className="text-sm text-muted-foreground">{row.getValue("lastModified")}</div>;
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            Edit
          </Button>
          <Button variant="outline" size="sm">
            Duplicate
          </Button>
        </div>
      ),
    },
  ];

  const table = useReactTable({
    data: estimates,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
      globalFilter,
    },
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Estimates</h1>
          <p className="text-muted-foreground">Manage your construction estimates</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            Import Excel
          </Button>
          <Button>
            + New Estimate
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search Estimates</CardTitle>
          <CardDescription>Find estimates by name, client, or status</CardDescription>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="Search estimates..."
            value={globalFilter ?? ""}
            onChange={(event) => setGlobalFilter(event.target.value)}
            className="max-w-sm"
          />
        </CardContent>
      </Card>

      {/* Estimates Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Estimates</CardTitle>
          <CardDescription>
            {table.getFilteredRowModel().rows.length} estimates found
          </CardDescription>
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
                      No estimates found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
