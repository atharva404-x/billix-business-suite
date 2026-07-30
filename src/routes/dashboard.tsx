import { createFileRoute, Link } from "@tanstack/react-router";
import {
  IndianRupee,
  ReceiptText,
  Wallet,
  Plus,
  ArrowUpRight,
  Package,
  Users,
  Calendar,
} from "lucide-react";
import { useUser } from "@clerk/tanstack-react-start";
import { useBusiness } from "@/hooks/use-business";
import { useBusinessQuery } from "@/hooks/use-api";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
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
import { ChartPlaceholder, ChartSalesItem } from "@/components/common/chart-placeholder";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "Dashboard — Billix" }] }),
  component: Dashboard,
});

interface DashboardSummary {
  sales_today: number;
  sales_this_week: number;
  sales_this_month: number;
  sales_this_year: number;
  outstanding_receivables: number;
  total_customers: number;
  total_suppliers: number;
  total_products: number;
  active_products: number;
  out_of_stock_products: number;
  low_stock_products: number;
  inventory_value: number;
  paid_invoices: number;
  pending_invoices: number;
  cancelled_invoices: number;
  total_revenue: number;
  average_invoice_value: number;
}

interface TopSellingProductItem {
  product_id: string;
  product_name: string;
  quantity_sold: number;
  total_revenue: number;
}

interface RecentInvoiceItem {
  invoice_id: string;
  invoice_number: string;
  customer_id: string;
  customer_name: string;
  total_amount: number;
  status: string;
  invoice_date: string;
}

interface DashboardData {
  summary: DashboardSummary;
  top_selling_products: TopSellingProductItem[];
  recent_invoices: RecentInvoiceItem[];
}

interface SalesReportResponse {
  items: ChartSalesItem[];
}

function Dashboard() {
  const { user } = useUser();
  const { activeBusiness, activeBusinessName } = useBusiness();

  // 1. Fetch Core Dashboard KPI and invoice lists
  const {
    data: dashboardData,
    isLoading: dashboardLoading,
    error: dashboardError,
    refetch: refetchDashboard,
  } = useBusinessQuery<DashboardData>(["dashboard"], API_ENDPOINTS.dashboard);

  // 2. Fetch Monthly Sales Overview graph history
  const {
    data: salesData,
    isLoading: salesLoading,
    error: salesError,
    refetch: refetchSales,
  } = useBusinessQuery<SalesReportResponse>(
    ["sales", "monthly"],
    `${API_ENDPOINTS.reports.sales}?group_by=month`,
  );

  const getGreeting = () => {
    const hr = new Date().getHours();
    if (hr < 12) return "Good morning";
    if (hr < 17) return "Good afternoon";
    return "Good evening";
  };

  const handleRetryAll = () => {
    refetchDashboard();
    refetchSales();
  };

  // Render high-fidelity skeleton cards and tables on initial query resolve
  if (dashboardLoading || salesLoading) {
    return <DashboardSkeleton />;
  }

  // Handle server connection error states
  if (dashboardError || salesError) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load dashboard workspace"
            description={
              dashboardError?.message ||
              salesError?.message ||
              "Could not communicate with Billix analytics endpoints."
            }
            onRetry={handleRetryAll}
          />
        </div>
      </AppShell>
    );
  }

  const summary = dashboardData?.summary;
  const recentInvoicesList = dashboardData?.recent_invoices || [];
  const chartData = salesData?.items || [];

  const totalInvoices = (summary?.paid_invoices || 0) + (summary?.pending_invoices || 0);

  return (
    <AppShell>
      <PageHeader
        title={`${getGreeting()}, ${user?.firstName || "Partner"}`}
        description={`Here's what's happening at ${activeBusinessName || "your business"} today.`}
        actions={
          <>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Calendar className="h-4 w-4" /> This month
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
          value={`₹${(summary?.total_revenue || 0).toLocaleString("en-IN")}`}
          change=""
          trend="up"
          hint="all-time cumulative"
          icon={IndianRupee}
        />
        <KpiCard
          label="Invoices Raised"
          value={totalInvoices.toLocaleString("en-IN")}
          change=""
          trend="up"
          hint="active raised profiles"
          icon={ReceiptText}
        />
        <KpiCard
          label="Outstanding Receivables"
          value={`₹${(summary?.outstanding_receivables || 0).toLocaleString("en-IN")}`}
          change=""
          trend="down"
          hint="pending invoice collections"
          icon={Wallet}
        />
        <KpiCard
          label="Average Invoice"
          value={`₹${(summary?.average_invoice_value || 0).toLocaleString("en-IN")}`}
          change=""
          trend="up"
          hint="average checkout size"
          icon={IndianRupee}
        />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Sales overview</CardTitle>
              <p className="text-xs text-muted-foreground">Compare monthly revenue and target</p>
            </div>
            <Button asChild variant="ghost" size="sm" className="gap-1">
              <Link to="/reports">
                View report <ArrowUpRight className="h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <ChartPlaceholder data={chartData} />
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
        <CardContent className={recentInvoicesList.length === 0 ? "p-6" : "p-0"}>
          {recentInvoicesList.length === 0 ? (
            <EmptyState
              title="No invoices raised yet"
              description="Create your very first invoice profile to begin billing clients."
              actionText="Create Invoice"
              onActionClick={() => {
                // Programmatic redirection triggers TanStack link
                window.location.hash = "/invoices/new";
              }}
            />
          ) : (
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
                  {recentInvoicesList.map((r) => (
                    <TableRow key={r.invoice_id}>
                      <TableCell className="font-medium">
                        <Link
                          to="/invoices/$id"
                          params={{ id: r.invoice_id }}
                          className="text-primary hover:underline font-semibold"
                        >
                          {r.invoice_number}
                        </Link>
                      </TableCell>
                      <TableCell>{r.customer_name}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(r.invoice_date).toLocaleDateString("en-IN")}
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        ₹{r.total_amount.toLocaleString("en-IN")}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={r.status} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}

function DashboardSkeleton() {
  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="h-8 w-64 animate-pulse rounded bg-muted/60" />
            <div className="h-4 w-96 animate-pulse rounded bg-muted/60" />
          </div>
          <div className="flex items-center gap-2">
            <div className="h-9 w-24 animate-pulse rounded bg-muted/60" />
            <div className="h-9 w-32 animate-pulse rounded bg-muted/60" />
          </div>
        </div>

        {/* KPI Cards Skeleton */}
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="rounded-xl border bg-card p-6 shadow-sm">
              <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-4 w-24 animate-pulse rounded bg-muted/60" />
                <div className="h-8 w-8 animate-pulse rounded-full bg-muted/60" />
              </div>
              <div className="mt-2 space-y-2">
                <div className="h-8 w-32 animate-pulse rounded bg-muted/60" />
                <div className="h-4 w-40 animate-pulse rounded bg-muted/60" />
              </div>
            </div>
          ))}
        </div>

        {/* Middle Section Skeleton */}
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border bg-card p-6 shadow-sm lg:col-span-2 space-y-4">
            <div className="space-y-2">
              <div className="h-5 w-40 animate-pulse rounded bg-muted/60" />
              <div className="h-4 w-60 animate-pulse rounded bg-muted/60" />
            </div>
            <div className="h-[260px] w-full animate-pulse rounded bg-muted/30" />
          </div>
          <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
            <div className="h-5 w-32 animate-pulse rounded bg-muted/60" />
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-10 w-full animate-pulse rounded bg-muted/40" />
              ))}
            </div>
          </div>
        </div>

        {/* Table Section Skeleton */}
        <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
          <div className="space-y-2">
            <div className="h-5 w-36 animate-pulse rounded bg-muted/60" />
            <div className="h-4 w-48 animate-pulse rounded bg-muted/60" />
          </div>
          <div className="space-y-2 pt-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 w-full animate-pulse rounded bg-muted/30" />
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
