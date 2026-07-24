import { createFileRoute, Link } from "@tanstack/react-router";
import {
  IndianRupee,
  ReceiptText,
  Wallet,
  Percent,
  Plus,
  ArrowUpRight,
  Package,
  Users,
} from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { KpiCard } from "@/components/common/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/common/status-badge";
import { ChartPlaceholder } from "@/components/common/chart-placeholder";
import { recentInvoices } from "@/lib/mock-data";

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "Dashboard — Billix" }] }),
  component: Dashboard,
});

function Dashboard() {
  return (
    <AppShell>
      <PageHeader
        title="Good morning, Rahul"
        description="Here's what's happening at Sharma Retail Store today."
        actions={
          <>
            <Button variant="outline" size="sm">
              This month
            </Button>
            <Button asChild size="sm" className="gap-1.5">
              <Link to="/invoices/new">
                <Plus className="h-4 w-4" /> New Invoice
              </Link>
            </Button>
          </>
        }
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Total Revenue"
          value="₹12,84,500"
          change="+12.4%"
          trend="up"
          hint="vs last month"
          icon={IndianRupee}
        />
        <KpiCard
          label="Invoices Raised"
          value="1,284"
          change="+8.1%"
          trend="up"
          hint="this month"
          icon={ReceiptText}
        />
        <KpiCard
          label="Outstanding"
          value="₹1,42,800"
          change="-4.2%"
          trend="down"
          hint="receivables"
          icon={Wallet}
        />
        <KpiCard
          label="GST Collected"
          value="₹2,31,210"
          change="+6.7%"
          trend="up"
          hint="current cycle"
          icon={Percent}
        />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Sales overview</CardTitle>
              <p className="text-xs text-muted-foreground">Compare monthly revenue and target</p>
            </div>
            <Button variant="ghost" size="sm" className="gap-1">
              View report <ArrowUpRight className="h-3.5 w-3.5" />
            </Button>
          </CardHeader>
          <CardContent>
            <ChartPlaceholder />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <Button asChild variant="outline" className="justify-start gap-2">
              <Link to="/invoices/new">
                <Plus className="h-4 w-4" /> Create GST invoice
              </Link>
            </Button>
            <Button asChild variant="outline" className="justify-start gap-2">
              <Link to="/products">
                <Package className="h-4 w-4" /> Add product
              </Link>
            </Button>
            <Button asChild variant="outline" className="justify-start gap-2">
              <Link to="/customers">
                <Users className="h-4 w-4" /> Add customer
              </Link>
            </Button>
            <Button asChild variant="outline" className="justify-start gap-2">
              <Link to="/reports">
                <ReceiptText className="h-4 w-4" /> Generate GSTR-1
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent invoices</CardTitle>
            <p className="text-xs text-muted-foreground">Last 7 days activity</p>
          </div>
          <Button asChild variant="ghost" size="sm">
            <Link to="/invoices">View all</Link>
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice #</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentInvoices.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">{r.id}</TableCell>
                    <TableCell>{r.customer}</TableCell>
                    <TableCell className="text-muted-foreground">{r.date}</TableCell>
                    <TableCell className="text-right font-semibold">{r.amount}</TableCell>
                    <TableCell>
                      <StatusBadge status={r.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
