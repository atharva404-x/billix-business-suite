import { createFileRoute } from "@tanstack/react-router";
import { Plus, ArrowUpDown, Boxes, AlertTriangle, TrendingDown } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DataToolbar } from "@/components/common/data-toolbar";
import { SimplePagination } from "@/components/common/simple-pagination";
import { KpiCard } from "@/components/common/kpi-card";
import { StatusBadge } from "@/components/common/status-badge";
import { products } from "@/lib/mock-data";

export const Route = createFileRoute("/inventory")({
  head: () => ({ meta: [{ title: "Inventory — Billix" }] }),
  component: InventoryPage,
});

function status(n: number) {
  if (n === 0) return "Out of Stock";
  if (n < 15) return "Low Stock";
  return "In Stock";
}

function InventoryPage() {
  return (
    <AppShell>
      <PageHeader
        title="Inventory"
        description="Live stock levels, movements and low-stock alerts."
        actions={
          <>
            <Button variant="outline" size="sm" className="gap-1.5"><ArrowUpDown className="h-4 w-4" /> Stock Transfer</Button>
            <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" /> Adjust Stock</Button>
          </>
        }
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Items in Stock" value="1,182" icon={Boxes} />
        <KpiCard label="Low Stock" value="24" icon={AlertTriangle} trend="down" change="review" />
        <KpiCard label="Dead Stock" value="6" icon={TrendingDown} />
      </div>
      <Card>
        <CardContent className="p-4 md:p-6">
          <DataToolbar placeholder="Search stock…" />
          <div className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>SKU</TableHead>
                  <TableHead className="text-right">On Hand</TableHead>
                  <TableHead className="text-right">Reorder At</TableHead>
                  <TableHead className="text-right">Value</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell className="font-medium">{p.name}</TableCell>
                    <TableCell className="font-mono text-xs">{p.sku}</TableCell>
                    <TableCell className="text-right">{p.stock} {p.unit}</TableCell>
                    <TableCell className="text-right text-muted-foreground">15</TableCell>
                    <TableCell className="text-right font-semibold">{p.price}</TableCell>
                    <TableCell><StatusBadge status={status(p.stock)} /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <SimplePagination total={1182} />
        </CardContent>
      </Card>
    </AppShell>
  );
}