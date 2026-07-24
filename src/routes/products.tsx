import { createFileRoute } from "@tanstack/react-router";
import { Plus, MoreHorizontal, Package } from "lucide-react";
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
import { Badge } from "@/components/ui/badge";
import { DataToolbar } from "@/components/common/data-toolbar";
import { SimplePagination } from "@/components/common/simple-pagination";
import { KpiCard } from "@/components/common/kpi-card";
import { StatusBadge } from "@/components/common/status-badge";
import { products } from "@/lib/mock-data";

export const Route = createFileRoute("/products")({
  head: () => ({ meta: [{ title: "Products — Billix" }] }),
  component: ProductsPage,
});

function stockStatus(n: number) {
  if (n === 0) return "Out of Stock";
  if (n < 15) return "Low Stock";
  return "In Stock";
}

function ProductsPage() {
  return (
    <AppShell>
      <PageHeader
        title="Products"
        description="Your item catalogue with pricing, GST and stock."
        actions={
          <Button className="gap-1.5">
            <Plus className="h-4 w-4" /> Add Product
          </Button>
        }
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard label="Total SKUs" value="1,206" icon={Package} />
        <KpiCard label="Categories" value="18" />
        <KpiCard label="Low Stock" value="24" trend="down" change="attention" />
        <KpiCard label="Inventory Value" value="₹34,20,000" trend="up" change="+2.1%" />
      </div>
      <Card>
        <CardContent className="p-4 md:p-6">
          <DataToolbar placeholder="Search products by name, SKU or HSN…" />
          <div className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>SKU</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                  <TableHead>GST</TableHead>
                  <TableHead className="text-right">Stock</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>
                      <div className="font-medium">{p.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {p.id} · {p.unit}
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{p.sku}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{p.category}</Badge>
                    </TableCell>
                    <TableCell className="text-right font-semibold">{p.price}</TableCell>
                    <TableCell>{p.gst}</TableCell>
                    <TableCell className="text-right">{p.stock}</TableCell>
                    <TableCell>
                      <StatusBadge status={stockStatus(p.stock)} />
                    </TableCell>
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
          <SimplePagination total={1206} />
        </CardContent>
      </Card>
    </AppShell>
  );
}
