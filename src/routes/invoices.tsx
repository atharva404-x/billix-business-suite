import { createFileRoute, Link } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
import {
  Plus,
  MoreHorizontal,
  Eye,
  Search,
  SlidersHorizontal,
  Download,
  FileText,
  ArrowUpDown,
  Copy,
} from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useBusiness } from "@/hooks/use-business";
import { useBusinessQuery } from "@/hooks/use-api";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

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
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { SimplePagination } from "@/components/common/simple-pagination";
import { StatusBadge } from "@/components/common/status-badge";
import { KpiCard } from "@/components/common/kpi-card";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

import type { Customer } from "./customers";

export const Route = createFileRoute("/invoices")({
  head: () => ({ meta: [{ title: "Invoice History — Billix" }] }),
  component: InvoicesPage,
});

export interface InvoiceItem {
  id: string;
  invoice_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  discount?: number | null;
  gst_rate?: number | null;
  taxable_amount: number;
  tax_amount?: number | null;
  total: number;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: string;
  business_id: string;
  customer_id: string;
  invoice_number: string;
  invoice_date: string;
  due_date?: string | null;
  subtotal: number;
  discount_amount?: number | null;
  taxable_amount: number;
  cgst_amount?: number | null;
  sgst_amount?: number | null;
  igst_amount?: number | null;
  total_tax: number;
  round_off?: number | null;
  grand_total: number;
  outstanding_balance: number;
  payment_status: "UNPAID" | "PARTIALLY_PAID" | "PAID";
  status: "DRAFT" | "ISSUED" | "PAID" | "PARTIALLY_PAID" | "CANCELLED" | "VOID";
  notes?: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  items: InvoiceItem[];
}

interface InvoiceListResponse {
  items: Invoice[];
  total: number;
}

interface CustomerListResponse {
  items: Customer[];
  total: number;
}

function InvoicesPage() {
  const { activeBusinessId } = useBusiness();

  // 1. Filter and tab states
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [sortBy, setSortBy] = useState<"invoice_date" | "grand_total" | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // 2. Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  // 3. Query Invoices from backend API
  let statusFilter = "";
  if (activeTab === "paid") statusFilter = "&payment_status=PAID";
  else if (activeTab === "pending") statusFilter = "&payment_status=UNPAID";
  else if (activeTab === "draft") statusFilter = "&status=DRAFT";

  const { data, isLoading, error, refetch } = useBusinessQuery<InvoiceListResponse>(
    ["invoices", page, limit, debouncedSearch, activeTab, sortBy, sortOrder],
    `/api/v1/invoices?skip=${(page - 1) * limit}&limit=${limit}${statusFilter}${
      debouncedSearch ? `&search_query=${encodeURIComponent(debouncedSearch)}` : ""
    }${sortBy ? `&sort_by=${sortBy}&sort_order=${sortOrder}` : ""}`,
  );

  // 4. Query Customers to resolve IDs to names
  const { data: customersData } = useBusinessQuery<CustomerListResponse>(
    ["customers", "dropdown"],
    "/api/v1/customers?limit=100",
  );
  const customerMap = new Map((customersData?.items || []).map((c) => [c.id, c.name]));

  const handleSort = (field: "invoice_date" | "grand_total") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  // Render skeletons during loader transitions
  if (isLoading) {
    return <InvoicesSkeleton />;
  }

  // Handle server connection error states
  if (error) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load invoices"
            description={error.message || "Could not retrieve invoice records."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;

  // KPI computations derived directly from active backend response
  const totalSales = items.reduce(
    (sum, inv) => sum + (inv.status !== "CANCELLED" ? inv.grand_total : 0),
    0,
  );
  const totalPaid = items.reduce(
    (sum, inv) =>
      sum + (inv.status !== "CANCELLED" ? inv.grand_total - inv.outstanding_balance : 0),
    0,
  );
  const totalPending = items.reduce(
    (sum, inv) => sum + (inv.status !== "CANCELLED" ? inv.outstanding_balance : 0),
    0,
  );
  const cancelledCount = items.filter((inv) => inv.status === "CANCELLED").length;

  return (
    <AppShell>
      <PageHeader
        title="Invoices"
        description="All sales invoices, credit notes and payment histories."
        actions={
          <Button asChild className="gap-1.5 shadow-sm">
            <Link to="/invoices/new">
              <Plus className="h-4 w-4" /> New Invoice
            </Link>
          </Button>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard
          label="Total Sales Value"
          value={`₹${totalSales.toLocaleString("en-IN")}`}
          icon={FileText}
        />
        <KpiCard
          label="Total Collected"
          value={`₹${totalPaid.toLocaleString("en-IN")}`}
          trend="up"
        />
        <KpiCard
          label="Outstanding Due"
          value={`₹${totalPending.toLocaleString("en-IN")}`}
          trend="down"
          change={totalPending > 0 ? "pending" : ""}
        />
        <KpiCard label="Cancelled Invoices" value={cancelledCount.toLocaleString("en-IN")} />
      </div>

      <Card className="shadow-sm border">
        <CardContent className="p-4 md:p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <Tabs
              value={activeTab}
              onValueChange={(val) => {
                setActiveTab(val);
                setPage(1);
              }}
            >
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="paid">Paid</TabsTrigger>
                <TabsTrigger value="pending">Pending</TabsTrigger>
                <TabsTrigger value="draft">Drafts</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
            <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by invoice # or customer…"
                className="h-9 pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Button variant="outline" size="sm" className="gap-1.5">
                <SlidersHorizontal className="h-4 w-4" />{" "}
                <span className="hidden sm:inline">Filter</span>
              </Button>
            </div>
          </div>

          {items.length === 0 ? (
            <EmptyState
              title={search ? "No matching invoices found" : "No invoices created yet"}
              description={
                search
                  ? "Try refining your search keyword or invoice number."
                  : "Raise your first sales invoice to record customer billings and process payments."
              }
              actionText={search ? undefined : "Create First Invoice"}
              onActionClick={search ? undefined : () => (window.location.href = "/invoices/new")}
            />
          ) : (
            <>
              <div className="overflow-x-auto rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Invoice #</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          onClick={() => handleSort("invoice_date")}
                          className="h-8 gap-1 p-0 hover:bg-transparent font-semibold text-xs"
                        >
                          Invoice Date <ArrowUpDown className="h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead className="text-right">
                        <Button
                          variant="ghost"
                          onClick={() => handleSort("grand_total")}
                          className="h-8 gap-1 p-0 hover:bg-transparent font-semibold text-xs ml-auto"
                        >
                          Grand Total <ArrowUpDown className="h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>Payment Status</TableHead>
                      <TableHead>Invoice Status</TableHead>
                      <TableHead className="w-16 text-right" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((r) => {
                      const customerName = customerMap.get(r.customer_id) || "Customer Profile";

                      return (
                        <TableRow key={r.id}>
                          <TableCell className="font-semibold font-mono">
                            <Link
                              to="/invoices/$id"
                              params={{ id: r.id }}
                              className="text-primary hover:underline"
                            >
                              {r.invoice_number}
                            </Link>
                          </TableCell>
                          <TableCell className="font-medium">{customerName}</TableCell>
                          <TableCell className="text-muted-foreground text-xs">
                            {new Date(r.invoice_date).toLocaleDateString("en-IN")}
                          </TableCell>
                          <TableCell className="text-right font-bold text-foreground">
                            ₹
                            {r.grand_total.toLocaleString("en-IN", {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </TableCell>
                          <TableCell>
                            <StatusBadge
                              status={
                                r.payment_status === "PAID"
                                  ? "Paid"
                                  : r.payment_status === "PARTIALLY_PAID"
                                    ? "Partially Paid"
                                    : "Unpaid"
                              }
                            />
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={r.status === "CANCELLED" ? "destructive" : "outline"}
                              className="text-[10px]"
                            >
                              {r.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button
                                asChild
                                variant="ghost"
                                size="icon"
                                title="View Details"
                                className="h-8 w-8 cursor-pointer"
                              >
                                <Link to="/invoices/$id" params={{ id: r.id }}>
                                  <Eye className="h-4 w-4" />
                                </Link>
                              </Button>
                              <Button
                                asChild
                                variant="ghost"
                                size="icon"
                                title="Duplicate Invoice"
                                className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                              >
                                <Link to="/invoices/new">
                                  <Copy className="h-4 w-4" />
                                </Link>
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>

              <SimplePagination
                total={total}
                page={page}
                pageSize={limit}
                onPageChange={(p) => setPage(p)}
              />
            </>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}

function InvoicesSkeleton() {
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
              <div className="flex flex-row items-center justify-between pb-2">
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

        <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
          <div className="h-9 w-64 animate-pulse rounded bg-muted/60" />
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
