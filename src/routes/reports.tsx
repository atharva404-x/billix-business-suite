import { createFileRoute } from "@tanstack/react-router";
import { Download, FileText, IndianRupee, Percent, Wallet } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChartPlaceholder } from "@/components/common/chart-placeholder";
import { KpiCard } from "@/components/common/kpi-card";

export const Route = createFileRoute("/reports")({
  head: () => ({ meta: [{ title: "Reports — Billix" }] }),
  component: ReportsPage,
});

const gstReports = [
  { code: "GSTR-1", name: "Outward supplies", period: "Jun 2026", status: "Ready" },
  { code: "GSTR-3B", name: "Summary return", period: "Jun 2026", status: "Draft" },
  { code: "GSTR-2B", name: "Inward supplies", period: "Jun 2026", status: "Ready" },
  { code: "HSN Summary", name: "HSN-wise sales", period: "Jun 2026", status: "Ready" },
];

function ReportsPage() {
  return (
    <AppShell>
      <PageHeader
        title="Reports"
        description="GST filings, sales & purchase, P&L and stock reports."
        actions={<Button variant="outline" size="sm" className="gap-1.5"><Download className="h-4 w-4" /> Export all</Button>}
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Sales (MTD)" value="₹12,84,500" icon={IndianRupee} trend="up" change="+12.4%" />
        <KpiCard label="GST Payable" value="₹2,31,210" icon={Percent} trend="up" change="+6.7%" />
        <KpiCard label="Net Profit" value="₹3,84,200" icon={Wallet} trend="up" change="+9.1%" />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Sales vs Purchase</CardTitle></CardHeader>
          <CardContent><ChartPlaceholder label="Trend" /></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>GST Reports</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {gstReports.map((r) => (
              <div key={r.code} className="flex items-center justify-between rounded-xl border bg-card p-4">
                <div className="flex items-center gap-3">
                  <div className="grid h-10 w-10 place-items-center rounded-lg bg-primary/10 text-primary"><FileText className="h-5 w-5" /></div>
                  <div>
                    <div className="font-semibold">{r.code} <span className="ml-2 text-xs font-normal text-muted-foreground">{r.name}</span></div>
                    <div className="text-xs text-muted-foreground">Period: {r.period} · {r.status}</div>
                  </div>
                </div>
                <Button variant="outline" size="sm">Download</Button>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}