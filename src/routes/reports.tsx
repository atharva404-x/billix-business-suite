import { createFileRoute } from "@tanstack/react-router";
import React, { useState } from "react";
import {
  Download,
  FileText,
  IndianRupee,
  Percent,
  Wallet,
  Printer,
  FileSpreadsheet,
  RefreshCw,
  Search,
  CheckCircle,
  TrendingUp,
} from "lucide-react";
import { useBusinessQuery } from "@/hooks/use-api";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
import { toast } from "sonner";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { KpiCard } from "@/components/common/kpi-card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ChartPlaceholder, ChartSalesItem } from "@/components/common/chart-placeholder";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

export const Route = createFileRoute("/reports")({
  head: () => ({ meta: [{ title: "Reports & GST Compliance — Billix" }] }),
  component: ReportsPage,
});

interface GstReportItem {
  invoice_id: string;
  invoice_number: string;
  invoice_date: string;
  customer_name: string;
  customer_gstin?: string | null;
  place_of_supply?: string | null;
  taxable_amount: number;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
  total_tax: number;
  grand_total: number;
}

interface GstReportResponse {
  total_taxable_amount: number;
  total_cgst: number;
  total_sgst: number;
  total_igst: number;
  total_gst: number;
  items: GstReportItem[];
}

interface SalesReportResponse {
  items: ChartSalesItem[];
}

function ReportsPage() {
  const [activeTab, setActiveTab] = useState("gst");
  const [search, setSearch] = useState("");

  // 1. Fetch GST Compliance Report
  const {
    data: gstData,
    isLoading: gstLoading,
    error: gstError,
    refetch: refetchGst,
  } = useBusinessQuery<GstReportResponse>(["reports", "gst"], "/api/v1/reports/gst");

  // 2. Fetch Sales Trend Report
  const {
    data: salesData,
    isLoading: salesLoading,
    error: salesError,
    refetch: refetchSales,
  } = useBusinessQuery<SalesReportResponse>(
    ["reports", "sales"],
    `${API_ENDPOINTS.reports.sales}?group_by=month`,
  );

  const handleRetryAll = () => {
    refetchGst();
    refetchSales();
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportCSV = () => {
    const items = gstData?.items || [];
    if (items.length === 0) {
      toast.error("No report data available to export.");
      return;
    }
    const headers = [
      "Invoice Number",
      "Invoice Date",
      "Customer Name",
      "Customer GSTIN",
      "Place of Supply",
      "Taxable Amount",
      "CGST Amount",
      "SGST Amount",
      "IGST Amount",
      "Total Tax",
      "Grand Total",
    ];
    const rows = items.map((r) => [
      `"${r.invoice_number}"`,
      `"${new Date(r.invoice_date).toLocaleDateString("en-IN")}"`,
      `"${r.customer_name.replace(/"/g, '""')}"`,
      `"${r.customer_gstin || ""}"`,
      `"${r.place_of_supply || ""}"`,
      r.taxable_amount,
      r.cgst_amount,
      r.sgst_amount,
      r.igst_amount,
      r.total_tax,
      r.grand_total,
    ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `gst_report_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("GST Report exported to CSV.");
  };

  if (gstLoading || salesLoading) {
    return <ReportsSkeleton />;
  }

  if (gstError || salesError) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load reports workspace"
            description="Could not generate GST compliance report tables."
            onRetry={handleRetryAll}
          />
        </div>
      </AppShell>
    );
  }

  const gstItems = (gstData?.items || []).filter(
    (item) =>
      item.invoice_number.toLowerCase().includes(search.toLowerCase()) ||
      item.customer_name.toLowerCase().includes(search.toLowerCase()) ||
      (item.customer_gstin && item.customer_gstin.toLowerCase().includes(search.toLowerCase())),
  );

  return (
    <AppShell>
      <PageHeader
        title="Reports & GST Compliance"
        description="GSTR filings, tax ledgers, outward supplies and sales audit registers."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handlePrint} className="gap-1.5 shadow-sm">
              <Printer className="h-4 w-4" /> Print Report
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCSV}
              className="gap-1.5 shadow-sm"
            >
              <Download className="h-4 w-4" /> Export CSV
            </Button>
          </div>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard
          label="Total Taxable Sales"
          value={`₹${(gstData?.total_taxable_amount || 0).toLocaleString("en-IN")}`}
          icon={IndianRupee}
          hint="base taxable value"
        />
        <KpiCard
          label="CGST Liability"
          value={`₹${(gstData?.total_cgst || 0).toLocaleString("en-IN")}`}
          icon={Percent}
          hint="central tax collected"
        />
        <KpiCard
          label="SGST Liability"
          value={`₹${(gstData?.total_sgst || 0).toLocaleString("en-IN")}`}
          icon={Percent}
          hint="state tax collected"
        />
        <KpiCard
          label="IGST Liability"
          value={`₹${(gstData?.total_igst || 0).toLocaleString("en-IN")}`}
          icon={Wallet}
          hint="integrated tax collected"
        />
      </div>

      <Tabs defaultValue="gst" value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2 lg:w-96">
          <TabsTrigger value="gst">GST Tax Register</TabsTrigger>
          <TabsTrigger value="sales">Sales Overview</TabsTrigger>
        </TabsList>

        <TabsContent value="gst" className="space-y-4">
          <Card className="shadow-sm border">
            <CardHeader className="flex flex-row items-center justify-between py-4">
              <CardTitle className="text-base font-bold">GSTR-1 Outward Tax Register</CardTitle>
              <div className="relative w-64">
                <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filter by invoice, customer or GSTIN…"
                  className="h-8 pl-8 text-xs"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {gstItems.length === 0 ? (
                <div className="p-6">
                  <EmptyState
                    title="No tax records found"
                    description="Issue GST billing invoices to generate tax compliance registers."
                  />
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Invoice #</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Customer</TableHead>
                        <TableHead>GSTIN</TableHead>
                        <TableHead className="text-right">Taxable Amt</TableHead>
                        <TableHead className="text-right">CGST</TableHead>
                        <TableHead className="text-right">SGST</TableHead>
                        <TableHead className="text-right">IGST</TableHead>
                        <TableHead className="text-right">Total Tax</TableHead>
                        <TableHead className="text-right">Grand Total</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {gstItems.map((r) => (
                        <TableRow key={r.invoice_id}>
                          <TableCell className="font-mono text-xs font-semibold text-primary">
                            {r.invoice_number}
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {new Date(r.invoice_date).toLocaleDateString("en-IN")}
                          </TableCell>
                          <TableCell className="font-medium text-xs">{r.customer_name}</TableCell>
                          <TableCell className="font-mono text-xs">
                            {r.customer_gstin || (
                              <span className="text-muted-foreground/40">—</span>
                            )}
                          </TableCell>
                          <TableCell className="text-right font-medium text-xs">
                            ₹{r.taxable_amount.toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell className="text-right text-xs">
                            ₹{r.cgst_amount.toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell className="text-right text-xs">
                            ₹{r.sgst_amount.toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell className="text-right text-xs">
                            ₹{r.igst_amount.toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell className="text-right font-semibold text-xs text-primary">
                            ₹{r.total_tax.toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell className="text-right font-bold text-xs">
                            ₹{r.grand_total.toLocaleString("en-IN")}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sales" className="space-y-4">
          <Card className="shadow-sm border">
            <CardHeader>
              <CardTitle className="text-base font-bold">Monthly Sales Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartPlaceholder data={salesData?.items || []} label="Sales Revenue History" />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}

function ReportsSkeleton() {
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

        <div className="rounded-xl border bg-card p-6 shadow-sm animate-pulse h-96" />
      </div>
    </AppShell>
  );
}
