import { createFileRoute } from "@tanstack/react-router";
import { Plus, MoreHorizontal, Truck } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataToolbar } from "@/components/common/data-toolbar";
import { SimplePagination } from "@/components/common/simple-pagination";
import { KpiCard } from "@/components/common/kpi-card";
import { suppliers } from "@/lib/mock-data";

export const Route = createFileRoute("/suppliers")({
  head: () => ({ meta: [{ title: "Suppliers — Billix" }] }),
  component: SuppliersPage,
});

function SuppliersPage() {
  return (
    <AppShell>
      <PageHeader
        title="Suppliers"
        description="Vendors, purchase orders and payables in one place."
        actions={
          <Button className="gap-1.5">
            <Plus className="h-4 w-4" /> Add Supplier
          </Button>
        }
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Total Suppliers" value="64" icon={Truck} />
        <KpiCard label="Payables" value="₹2,18,400" trend="up" change="+3.1%" hint="unpaid bills" />
        <KpiCard label="Purchase MTD" value="₹6,84,200" trend="up" change="+9.4%" />
      </div>
      <Card>
        <CardContent className="p-4 md:p-6">
          <DataToolbar placeholder="Search suppliers…" />
          <div className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Supplier</TableHead>
                  <TableHead>GSTIN</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>City</TableHead>
                  <TableHead className="text-right">Payable</TableHead>
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {suppliers.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>
                      <div className="font-medium">{s.name}</div>
                      <div className="text-xs text-muted-foreground">{s.id}</div>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{s.gstin}</TableCell>
                    <TableCell>{s.phone}</TableCell>
                    <TableCell>{s.city}</TableCell>
                    <TableCell className="text-right font-semibold">{s.payable}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <SimplePagination total={64} />
        </CardContent>
      </Card>
    </AppShell>
  );
}
