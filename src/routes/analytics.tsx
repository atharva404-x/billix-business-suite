import { createFileRoute } from "@tanstack/react-router";
import React, { useState } from "react";
import { TrendingUp, Users, Package, DollarSign, Calendar, RefreshCw } from "lucide-react";
import { useBusinessQuery } from "@/hooks/use-api";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartPlaceholder, ChartSalesItem } from "@/components/common/chart-placeholder";
import { KpiCard } from "@/components/common/kpi-card";
import { Button } from "@/components/ui/button";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

export const Route = createFileRoute("/analytics")({
  head: () => ({ meta: [{ title: "Analytics — Billix" }] }),
  component: AnalyticsPage,
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

interface TopCustomerItem {
  customer_id: string;
  customer_name: string;
  total_spent: number;
  invoice_count: number;
}

interface DashboardResponse {
  summary: DashboardSummary;
  top_selling_products: TopSellingProductItem[];
}

interface SalesReportResponse {
  items: ChartSalesItem[];
}

interface CustomerReportResponse {
  top_customers?: TopCustomerItem[];
  items?: TopCustomerItem[];
}

function AnalyticsPage() {
  const [period, setPeriod] = useState<"month" | "year">("month");

  // 1. Core Summary KPI Data
  const {
    data: dashData,
    isLoading: dashLoading,
    error: dashError,
    refetch: refetchDash,
  } = useBusinessQuery<DashboardResponse>(["analytics", "dashboard"], API_ENDPOINTS.dashboard);

  // 2. Revenue Trend Data
  const {
    data: salesData,
    isLoading: salesLoading,
    error: salesError,
    refetch: refetchSales,
  } = useBusinessQuery<SalesReportResponse>(
    ["analytics", "sales", period],
    `${API_ENDPOINTS.reports.sales}?group_by=${period}`,
  );

  // 3. Top Customers Report
  const {
    data: customerData,
    isLoading: custLoading,
    error: custError,
    refetch: refetchCust,
  } = useBusinessQuery<CustomerReportResponse>(
    ["analytics", "top_customers"],
    `${API_ENDPOINTS.reports.customers}?report_type=top`,
  );

  const handleRetry = () => {
    refetchDash();
    refetchSales();
    refetchCust();
  };

  if (dashLoading || salesLoading || custLoading) {
    return <AnalyticsSkeleton />;
  }

  if (dashError || salesError || custError) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load analytics workspace"
            description="Could not retrieve live business intelligence datasets from server."
            onRetry={handleRetry}
          />
        </div>
      </AppShell>
    );
  }

  const summary = dashData?.summary;
  const topProducts = dashData?.top_selling_products || [];
  const topCustomers = customerData?.top_customers || customerData?.items || [];
  const salesItems = salesData?.items || [];

  const maxCustSpent =
    topCustomers.length > 0 ? Math.max(...topCustomers.map((c) => c.total_spent), 1) : 1;

  return (
    <AppShell>
      <PageHeader
        title="Business Analytics"
        description="Deep insight into live revenue, top customers and product performance."
        actions={
          <div className="flex items-center gap-2">
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as "month" | "year")}
              className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
            >
              <option value="month">Monthly Breakdown</option>
              <option value="year">Yearly Breakdown</option>
            </select>
            <Button size="sm" variant="outline" onClick={handleRetry} className="gap-1.5 shadow-sm">
              <RefreshCw className="h-4 w-4" /> Refresh
            </Button>
          </div>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard
          label="Avg Checkout Value"
          value={`₹${(summary?.average_invoice_value || 0).toLocaleString("en-IN")}`}
          trend="up"
          change=""
          hint="live checkout size"
          icon={DollarSign}
        />
        <KpiCard
          label="Total Registered Clients"
          value={(summary?.total_customers || 0).toLocaleString("en-IN")}
          trend="up"
          change=""
          hint="active customer profiles"
          icon={Users}
        />
        <KpiCard
          label="Catalogued SKUs"
          value={(summary?.total_products || 0).toLocaleString("en-IN")}
          trend="up"
          change=""
          hint="active items"
          icon={Package}
        />
        <KpiCard
          label="Total Receivables"
          value={`₹${(summary?.outstanding_receivables || 0).toLocaleString("en-IN")}`}
          trend={summary?.outstanding_receivables ? "down" : "up"}
          change=""
          hint="unpaid invoice balances"
          icon={TrendingUp}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="shadow-sm border">
          <CardHeader>
            <CardTitle>Revenue trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartPlaceholder data={salesItems} label="Sales Revenue History" />
          </CardContent>
        </Card>

        <Card className="shadow-sm border">
          <CardHeader>
            <CardTitle>Top Selling Products</CardTitle>
          </CardHeader>
          <CardContent>
            {topProducts.length === 0 ? (
              <EmptyState
                title="No product sales recorded"
                description="Issue invoices with catalogued items to populate top product performance analytics."
              />
            ) : (
              <div className="space-y-4">
                {topProducts.map((p) => (
                  <div key={p.product_id} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold">{p.product_name}</span>
                      <span className="text-muted-foreground font-mono">
                        {p.quantity_sold} sold (₹{p.total_revenue.toLocaleString("en-IN")})
                      </span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{
                          width: `${Math.min(
                            100,
                            (p.total_revenue / (summary?.total_revenue || 1)) * 100 * 5,
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 shadow-sm border">
          <CardHeader>
            <CardTitle>Top Customers by Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            {topCustomers.length === 0 ? (
              <EmptyState
                title="No customer purchases yet"
                description="Register customer accounts and generate billing invoices to track customer lifetime values."
              />
            ) : (
              <div className="space-y-4">
                {topCustomers.map((c) => {
                  const percent = Math.max(0, Math.min(100, (c.total_spent / maxCustSpent) * 100));
                  return (
                    <div key={c.customer_id} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-semibold text-foreground">{c.customer_name}</span>
                        <span className="font-bold text-foreground">
                          ₹{c.total_spent.toLocaleString("en-IN")}
                        </span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${Math.max(percent, 4)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function AnalyticsSkeleton() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 animate-pulse rounded bg-muted/60" />
            <div className="h-4 w-80 animate-pulse rounded bg-muted/60" />
          </div>
          <div className="h-9 w-32 animate-pulse rounded bg-muted/60" />
        </div>

        <div className="grid gap-4 sm:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="rounded-xl border bg-card p-6 shadow-sm">
              <div className="h-4 w-24 animate-pulse rounded bg-muted/60 mb-2" />
              <div className="h-8 w-32 animate-pulse rounded bg-muted/60" />
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="h-72 rounded-xl border bg-card p-6 shadow-sm animate-pulse" />
          <div className="h-72 rounded-xl border bg-card p-6 shadow-sm animate-pulse" />
        </div>
      </div>
    </AppShell>
  );
}
