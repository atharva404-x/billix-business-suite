import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartPlaceholder } from "@/components/common/chart-placeholder";
import { KpiCard } from "@/components/common/kpi-card";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/analytics")({
  head: () => ({ meta: [{ title: "Analytics — Billix" }] }),
  component: AnalyticsPage,
});

function AnalyticsPage() {
  return (
    <AppShell>
      <PageHeader
        title="Analytics"
        description="Deep insight into revenue, customers and product performance."
        actions={
          <>
            <Button size="sm" variant="outline">
              Last 30 days
            </Button>
            <Button size="sm">Compare</Button>
          </>
        }
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard label="Avg. Order Value" value="₹1,842" trend="up" change="+4.2%" />
        <KpiCard label="Repeat Customers" value="38%" trend="up" change="+2.1pp" />
        <KpiCard label="Best Category" value="Hardware" hint="₹4.2L this month" />
        <KpiCard label="Fastest SKU" value="LED Bulb 9W" hint="128 units" />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Revenue trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartPlaceholder />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Category mix</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartPlaceholder label="Share by category" />
          </CardContent>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Top customers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { n: "Sharma Traders", v: "₹2,84,500", p: 82 },
                { n: "Krishna Hardware", v: "₹1,96,300", p: 64 },
                { n: "Deep Electricals", v: "₹1,52,800", p: 48 },
                { n: "Raj Medical Store", v: "₹98,120", p: 32 },
              ].map((c) => (
                <div key={c.n}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{c.n}</span>
                    <span className="text-muted-foreground">{c.v}</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-primary" style={{ width: `${c.p}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
