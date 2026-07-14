import { createFileRoute } from "@tanstack/react-router";
import { Plus, MoreHorizontal, Users } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { DataToolbar } from "@/components/common/data-toolbar";
import { SimplePagination } from "@/components/common/simple-pagination";
import { KpiCard } from "@/components/common/kpi-card";
import { customers } from "@/lib/mock-data";

export const Route = createFileRoute("/customers")({
  head: () => ({ meta: [{ title: "Customers — Billix" }] }),
  component: CustomersPage,
});

function CustomersPage() {
  return (
    <AppShell>
      <PageHeader
        title="Customers"
        description="Manage buyers, GSTINs, credit limits and outstanding balances."
        actions={<Button className="gap-1.5"><Plus className="h-4 w-4" /> Add Customer</Button>}
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Total Customers" value="482" hint="all businesses" icon={Users} />
        <KpiCard label="Outstanding" value="₹1,42,800" trend="down" change="-4.2%" hint="receivables" />
        <KpiCard label="New this month" value="26" trend="up" change="+18%" />
      </div>
      <Card>
        <CardContent className="p-4 md:p-6">
          <DataToolbar placeholder="Search customers by name, phone or GSTIN…" />
          <div className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Customer</TableHead>
                  <TableHead>GSTIN</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>City</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Balance</TableHead>
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {customers.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell>
                      <div className="font-medium">{c.name}</div>
                      <div className="text-xs text-muted-foreground">{c.id}</div>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{c.gstin}</TableCell>
                    <TableCell>{c.phone}</TableCell>
                    <TableCell>{c.city}</TableCell>
                    <TableCell><Badge variant="secondary">{c.type}</Badge></TableCell>
                    <TableCell className="text-right font-semibold">{c.balance}</TableCell>
                    <TableCell><Button variant="ghost" size="icon" className="h-8 w-8"><MoreHorizontal className="h-4 w-4" /></Button></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <SimplePagination total={482} />
        </CardContent>
      </Card>
    </AppShell>
  );
}