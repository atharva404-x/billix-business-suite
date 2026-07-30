import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import React, { useState } from "react";
import {
  ArrowLeft,
  Printer,
  Download,
  Send,
  CreditCard,
  Ban,
  CheckCircle2,
  Calendar,
  User,
  Building2,
  FileText,
  Trash2,
  Copy,
} from "lucide-react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { useBusiness } from "@/hooks/use-business";
import { useBusinessQuery } from "@/hooks/use-api";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
import { invalidateCache } from "@/lib/cache-invalidation";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { StatusBadge } from "@/components/common/status-badge";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { ErrorState } from "@/components/shared/api-states";

import type { Invoice } from "./invoices";
import type { Customer } from "./customers";
import type { Product } from "./products";

export const Route = createFileRoute("/invoices/$id")({
  head: () => ({ meta: [{ title: "Invoice Details — Billix" }] }),
  component: InvoiceDetails,
});

interface PaymentRecord {
  id: string;
  business_id: string;
  invoice_id: string;
  amount: number;
  payment_method: string;
  transaction_id?: string | null;
  notes?: string | null;
  created_by: string;
  created_at: string;
}

interface PaymentListResponse {
  items: PaymentRecord[];
  total: number;
}

interface ProductListResponse {
  items: Product[];
  total: number;
}

function InvoiceDetails() {
  const { id } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { activeBusiness } = useBusiness();

  const [paymentOpen, setPaymentOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  // Form states for Payment Modal
  const [paymentAmount, setPaymentAmount] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("CASH");
  const [transactionId, setTransactionId] = useState("");
  const [paymentNotes, setPaymentNotes] = useState("");

  // Form state for Cancellation Dialog
  const [cancelReason, setCancelReason] = useState("");

  // 1. Query Invoice Details
  const {
    data: invoice,
    isLoading,
    error,
    refetch,
  } = useBusinessQuery<Invoice>(["invoices", id], `/api/v1/invoices/${id}`);

  // 2. Query Customer Profile for invoice
  const { data: customer } = useBusinessQuery<Customer>(
    ["customers", invoice?.customer_id],
    `/api/v1/customers/${invoice?.customer_id}`,
    { enabled: !!invoice?.customer_id },
  );

  // 3. Query Product catalog to map item product_ids to product names
  const { data: productsData } = useBusinessQuery<ProductListResponse>(
    ["products", "dropdown"],
    "/api/v1/products?limit=100",
  );
  const productMap = new Map((productsData?.items || []).map((p) => [p.id, p]));

  // 4. Query Payment Records
  const { data: paymentsData, refetch: refetchPayments } = useBusinessQuery<PaymentListResponse>(
    ["payments", id],
    `/api/v1/invoices/${id}/payments`,
    { enabled: !!id },
  );

  // 5. Record Payment Mutation
  const recordPaymentMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => {
      return apiClient<PaymentRecord>("/api/v1/invoices/payments", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("invoice:create", queryClient);
      toast.success("Payment recorded successfully.");
      setPaymentOpen(false);
      setPaymentAmount("");
      setTransactionId("");
      setPaymentNotes("");
      refetch();
      refetchPayments();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to record payment.");
    },
  });

  // 6. Cancel Invoice Mutation
  const cancelInvoiceMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => {
      return apiClient<Invoice>(`/api/v1/invoices/${id}/cancel`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("invoice:cancel", queryClient);
      toast.success("Invoice cancelled & stock returned.");
      setCancelOpen(false);
      setCancelReason("");
      refetch();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to cancel invoice.");
    },
  });

  // 7. Delete Invoice Mutation
  const deleteInvoiceMutation = useMutation({
    mutationFn: () => {
      return apiClient(`/api/v1/invoices/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      invalidateCache("invoice:delete", queryClient);
      toast.success("Invoice deleted successfully.");
      navigate({ to: "/invoices" });
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to delete invoice.");
    },
  });

  if (isLoading) {
    return <InvoiceDetailsSkeleton />;
  }

  if (error || !invoice) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Invoice not found"
            description={error?.message || "The requested invoice could not be located."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  const handleOpenPaymentModal = () => {
    setPaymentAmount(invoice.outstanding_balance.toString());
    setPaymentOpen(true);
  };

  const handleRecordPaymentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const amt = parseFloat(paymentAmount);
    if (!amt || amt <= 0) {
      toast.error("Please enter a valid positive payment amount.");
      return;
    }
    if (amt > invoice.outstanding_balance) {
      toast.error("Payment amount cannot exceed outstanding balance.");
      return;
    }

    recordPaymentMutation.mutate({
      invoice_id: invoice.id,
      amount: amt,
      payment_method: paymentMethod,
      transaction_id: transactionId.trim() || null,
      notes: paymentNotes.trim() || null,
    });
  };

  const handleCancelSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cancelReason.trim()) {
      toast.error("Please specify a reason for cancellation.");
      return;
    }

    cancelInvoiceMutation.mutate({
      reason: cancelReason.trim(),
    });
  };

  const payments = paymentsData?.items || [];
  const isCancelled = invoice.status === "CANCELLED";

  return (
    <AppShell>
      <div className="print:hidden">
        <PageHeader
          title={`Invoice ${invoice.invoice_number}`}
          description={`Issued on ${new Date(invoice.invoice_date).toLocaleDateString("en-IN")}`}
          actions={
            <>
              <Button asChild variant="ghost" size="sm" className="gap-1.5">
                <Link to="/invoices">
                  <ArrowLeft className="h-4 w-4" /> Back
                </Link>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrint}
                className="gap-1.5 shadow-sm"
              >
                <Printer className="h-4 w-4" /> Print / PDF
              </Button>
              <Button asChild variant="outline" size="sm" className="gap-1.5 shadow-sm">
                <Link to="/invoices/new">
                  <Copy className="h-4 w-4" /> Duplicate
                </Link>
              </Button>
              {invoice.outstanding_balance > 0 && !isCancelled && (
                <Button size="sm" onClick={handleOpenPaymentModal} className="gap-1.5 shadow-sm">
                  <CreditCard className="h-4 w-4" /> Record Payment
                </Button>
              )}
              {!isCancelled && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCancelOpen(true)}
                  className="gap-1.5 shadow-sm text-destructive border-destructive/30 hover:bg-destructive/10"
                >
                  <Ban className="h-4 w-4" /> Cancel Invoice
                </Button>
              )}
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setDeleteOpen(true)}
                className="gap-1.5 shadow-sm"
              >
                <Trash2 className="h-4 w-4" /> Delete
              </Button>
            </>
          }
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px] print:block print:w-full">
        {/* Printable Tax Invoice Container */}
        <Card className="shadow-sm border print:shadow-none print:border-none">
          <CardContent className="p-6 md:p-8">
            <div className="flex flex-col justify-between gap-6 sm:flex-row">
              <div>
                <div className="font-display text-2xl font-bold text-foreground">
                  {activeBusiness?.business_name || "Business Suite"}
                </div>
                {activeBusiness?.gstin && (
                  <div className="mt-1 text-xs font-mono text-muted-foreground">
                    GSTIN: {activeBusiness.gstin}
                  </div>
                )}
                <div className="text-xs text-muted-foreground mt-1 max-w-xs">
                  {[
                    activeBusiness?.address,
                    activeBusiness?.city,
                    activeBusiness?.state,
                    activeBusiness?.pincode,
                  ]
                    .filter(Boolean)
                    .join(", ")}
                </div>
              </div>
              <div className="text-left sm:text-right">
                <div className="text-xs uppercase font-bold tracking-wider text-muted-foreground">
                  Tax Invoice
                </div>
                <div className="font-display text-xl font-bold font-mono text-primary">
                  {invoice.invoice_number}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  Date: {new Date(invoice.invoice_date).toLocaleDateString("en-IN")}
                </div>
                {invoice.due_date && (
                  <div className="text-xs text-muted-foreground">
                    Due Date: {new Date(invoice.due_date).toLocaleDateString("en-IN")}
                  </div>
                )}
                <div className="mt-2 flex gap-2 sm:justify-end">
                  <StatusBadge
                    status={
                      invoice.payment_status === "PAID"
                        ? "Paid"
                        : invoice.payment_status === "PARTIALLY_PAID"
                          ? "Partially Paid"
                          : "Unpaid"
                    }
                  />
                  {isCancelled && <Badge variant="destructive">Cancelled</Badge>}
                </div>
              </div>
            </div>

            <Separator className="my-6" />

            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <div className="text-xs uppercase font-bold tracking-wider text-muted-foreground">
                  Bill To
                </div>
                <div className="mt-1 font-semibold text-foreground">
                  {customer?.name || "Valued Customer"}
                </div>
                {customer?.gstin && (
                  <div className="text-xs font-mono text-muted-foreground">
                    GSTIN: {customer.gstin}
                  </div>
                )}
                <div className="text-xs text-muted-foreground mt-1">
                  {[customer?.address, customer?.city, customer?.state, customer?.pincode]
                    .filter(Boolean)
                    .join(", ") || "Address not provided"}
                </div>
              </div>
              <div className="sm:text-right">
                <div className="text-xs uppercase font-bold tracking-wider text-muted-foreground">
                  Place of Supply
                </div>
                <div className="mt-1 font-semibold text-foreground">
                  {customer?.state || activeBusiness?.state || "Intra-State"}
                </div>
              </div>
            </div>

            <div className="mt-8 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b text-left text-xs uppercase font-semibold text-muted-foreground bg-muted/30">
                  <tr>
                    <th className="py-2.5 px-2">Product Item</th>
                    <th className="text-right py-2.5 px-2">Qty</th>
                    <th className="text-right py-2.5 px-2">Rate (₹)</th>
                    <th className="text-right py-2.5 px-2">GST %</th>
                    <th className="text-right py-2.5 px-2">Tax (₹)</th>
                    <th className="text-right py-2.5 px-2">Total (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.items.map((item) => {
                    const prod = productMap.get(item.product_id);

                    return (
                      <tr key={item.id} className="border-b last:border-0 hover:bg-muted/10">
                        <td className="py-3 px-2 font-medium">
                          {prod?.name || "Product Record"}
                          {prod?.sku && (
                            <span className="ml-2 text-xs font-mono text-muted-foreground">
                              ({prod.sku})
                            </span>
                          )}
                        </td>
                        <td className="text-right py-3 px-2">{item.quantity}</td>
                        <td className="text-right py-3 px-2">₹{item.unit_price.toFixed(2)}</td>
                        <td className="text-right py-3 px-2">{item.gst_rate || 0}%</td>
                        <td className="text-right py-3 px-2">
                          ₹{(item.tax_amount || 0).toFixed(2)}
                        </td>
                        <td className="text-right py-3 px-2 font-semibold">
                          ₹
                          {item.total.toLocaleString("en-IN", {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="mt-6 flex justify-end">
              <div className="w-full max-w-xs space-y-2 text-sm">
                <DetailRow
                  label="Subtotal"
                  value={`₹${invoice.subtotal.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />
                {invoice.discount_amount && invoice.discount_amount > 0 && (
                  <DetailRow label="Discount" value={`-₹${invoice.discount_amount.toFixed(2)}`} />
                )}
                <DetailRow
                  label="Taxable Amount"
                  value={`₹${invoice.taxable_amount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />
                {invoice.cgst_amount && invoice.cgst_amount > 0 && (
                  <DetailRow label="CGST" value={`₹${invoice.cgst_amount.toFixed(2)}`} />
                )}
                {invoice.sgst_amount && invoice.sgst_amount > 0 && (
                  <DetailRow label="SGST" value={`₹${invoice.sgst_amount.toFixed(2)}`} />
                )}
                {invoice.igst_amount && invoice.igst_amount > 0 && (
                  <DetailRow label="IGST" value={`₹${invoice.igst_amount.toFixed(2)}`} />
                )}
                {invoice.round_off !== null && invoice.round_off !== undefined && (
                  <DetailRow label="Round Off" value={`₹${invoice.round_off.toFixed(2)}`} />
                )}
                <Separator />
                <div className="flex items-center justify-between font-display text-lg font-bold text-foreground">
                  <span>Grand Total</span>
                  <span>
                    ₹
                    {invoice.grand_total.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm font-semibold text-destructive pt-1">
                  <span>Balance Outstanding</span>
                  <span>
                    ₹
                    {invoice.outstanding_balance.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
              </div>
            </div>

            {invoice.notes && (
              <div className="mt-8 rounded-lg border p-4 bg-muted/20 text-xs">
                <div className="font-semibold text-muted-foreground mb-1">Notes & Terms:</div>
                <p className="text-foreground whitespace-pre-wrap">{invoice.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sidebar Payment Info & Audit Logs */}
        <div className="space-y-6 print:hidden">
          <Card className="shadow-sm border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Payment Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-xs text-muted-foreground">Grand Total</div>
                <div className="font-display text-xl font-bold">
                  ₹
                  {invoice.grand_total.toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </div>
              </div>
              <Separator />
              <div>
                <div className="text-xs text-muted-foreground">Outstanding Due</div>
                <div className="font-display text-2xl font-bold text-destructive">
                  ₹
                  {invoice.outstanding_balance.toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Payment History
              </CardTitle>
            </CardHeader>
            <CardContent>
              {payments.length === 0 ? (
                <p className="text-xs text-muted-foreground">
                  No payments recorded for this invoice yet.
                </p>
              ) : (
                <ul className="space-y-3 text-xs">
                  {payments.map((p) => (
                    <li key={p.id} className="p-2.5 rounded border bg-muted/20 space-y-1">
                      <div className="flex justify-between font-semibold">
                        <span>₹{p.amount.toFixed(2)}</span>
                        <Badge variant="outline" className="text-[10px]">
                          {p.payment_method}
                        </Badge>
                      </div>
                      <div className="text-muted-foreground text-[11px]">
                        Recorded on {new Date(p.created_at).toLocaleString("en-IN")}
                      </div>
                      {p.transaction_id && (
                        <div className="font-mono text-[10px] text-muted-foreground">
                          Txn #: {p.transaction_id}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Record Payment Dialog */}
      <Dialog open={paymentOpen} onOpenChange={setPaymentOpen}>
        <DialogContent className="sm:max-w-md">
          <form onSubmit={handleRecordPaymentSubmit}>
            <DialogHeader>
              <DialogTitle>Record Payment</DialogTitle>
              <DialogDescription>
                Record customer payment against Invoice {invoice.invoice_number}.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-1">
                <Label htmlFor="payment_amount">Payment Amount (₹) *</Label>
                <Input
                  id="payment_amount"
                  type="number"
                  step="any"
                  max={invoice.outstanding_balance}
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder="Enter amount"
                />
                <p className="text-xs text-muted-foreground">
                  Max balance: ₹{invoice.outstanding_balance.toFixed(2)}
                </p>
              </div>

              <div className="space-y-1">
                <Label htmlFor="payment_method">Payment Mode</Label>
                <select
                  id="payment_method"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                >
                  <option value="CASH">Cash</option>
                  <option value="UPI">UPI</option>
                  <option value="BANK_TRANSFER">Bank Transfer</option>
                  <option value="CHEQUE">Cheque</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>

              <div className="space-y-1">
                <Label htmlFor="transaction_id">Transaction ID / Reference Number</Label>
                <Input
                  id="transaction_id"
                  value={transactionId}
                  onChange={(e) => setTransactionId(e.target.value)}
                  placeholder="UTR / Cheque No."
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="payment_notes">Notes</Label>
                <Textarea
                  id="payment_notes"
                  rows={2}
                  value={paymentNotes}
                  onChange={(e) => setPaymentNotes(e.target.value)}
                  placeholder="Optional payment notes"
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setPaymentOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={recordPaymentMutation.isPending}>
                Save Payment
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Cancel Invoice Dialog */}
      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}>
        <DialogContent className="sm:max-w-md">
          <form onSubmit={handleCancelSubmit}>
            <DialogHeader>
              <DialogTitle className="text-destructive">Cancel Invoice</DialogTitle>
              <DialogDescription>
                Cancelling Invoice {invoice.invoice_number} will automatically reverse stock back
                into inventory.
              </DialogDescription>
            </DialogHeader>

            <div className="py-4 space-y-2">
              <Label htmlFor="cancel_reason">Cancellation Reason *</Label>
              <Textarea
                id="cancel_reason"
                rows={3}
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="Specify reason for cancelling this invoice..."
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setCancelOpen(false)}>
                Go Back
              </Button>
              <Button
                type="submit"
                variant="destructive"
                disabled={cancelInvoiceMutation.isPending}
              >
                Confirm Cancellation
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Invoice AlertDialog */}
      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Invoice permanently?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete Invoice {invoice.invoice_number}? This will
              permanently remove the invoice record and return items back to product inventory
              stock.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={() => deleteInvoiceMutation.mutate()}
            >
              {deleteInvoiceMutation.isPending ? "Deleting..." : "Delete Invoice"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </AppShell>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold text-foreground">{value}</span>
    </div>
  );
}

function InvoiceDetailsSkeleton() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div className="h-8 w-64 animate-pulse rounded bg-muted/60" />
        <div className="rounded-xl border bg-card p-8 shadow-sm space-y-6">
          <div className="flex justify-between">
            <div className="h-12 w-48 animate-pulse rounded bg-muted/60" />
            <div className="h-12 w-32 animate-pulse rounded bg-muted/60" />
          </div>
          <div className="h-40 w-full animate-pulse rounded bg-muted/30" />
        </div>
      </div>
    </AppShell>
  );
}
