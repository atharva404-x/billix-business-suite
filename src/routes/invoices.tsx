import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, MoreHorizontal, Eye } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataToolbar } from "@/components/common/data-toolbar";
import { SimplePagination } from "@/components/common/simple-pagination";
import { StatusBadge } from "@/components/common/status-badge";
import { KpiCard } from "@/components/common/kpi-card";
import { recentInvoices } from "@/lib/mock-data";

export const Route = createFileRoute("/invoices")({
  head: () => ({ meta: [{ title: "Invoice History — Billix" }] }),
  component: InvoicesPage,
});

function InvoicesPage() {
  return (
    <AppShell>
      <PageHeader
        title="Invoices"
        description="All sales invoices, credit notes and drafts."
        actions={<Button asChild className="gap-1.5"><Link to="/invoices/new"><Plus className="h-4 w-4" /> New Invoice</Link></Button>}
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard label="Total Sales" value="₹12,84,500" trend="up" change="+12.4%" />
        <KpiCard label="Paid" value="₹11,41,700" trend="up" change="+9.8%" />
        <KpiCard label="Pending" value="₹1,08,200" trend="up" change="+1.2%" />
        <KpiCard label="Overdue" value="₹34,600" trend="down" change="review" />
      </div>
      <Card>
        <CardContent className="p-4 md:p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="paid">Paid</TabsTrigger>
                <TabsTrigger value="pending">Pending</TabsTrigger>
                <TabsTrigger value="overdue">Overdue</TabsTrigger>
                <TabsTrigger value="draft">Drafts</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
          <div className="mt-4"><DataToolbar placeholder="Search by invoice #, customer…" /></div>
          <div className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-24" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentInvoices.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">{r.id}</TableCell>
                    <TableCell>{r.customer}</TableCell>
                    <TableCell className="text-muted-foreground">{r.date}</TableCell>
                    <TableCell className="text-right font-semibold">{r.amount}</TableCell>
                    <TableCell><StatusBadge status={r.status} /></TableCell>
                    <TableCell className="text-right">
                      <Button asChild variant="ghost" size="icon" className="h-8 w-8"><Link to="/invoices/$id" params={{ id: r.id }}><Eye className="h-4 w-4" /></Link></Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8"><MoreHorizontal className="h-4 w-4" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <SimplePagination total={1284} />
        </CardContent>
      </Card>
    </AppShell>
  );
}