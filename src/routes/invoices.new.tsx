import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import React, { useState } from "react";
import { Plus, Trash2, Save, Send, ArrowLeft, Info } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { ErrorState } from "@/components/shared/api-states";

import type { Customer } from "./customers";
import type { Product } from "./products";
import type { Invoice } from "./invoices";

export const Route = createFileRoute("/invoices/new")({
  head: () => ({ meta: [{ title: "New Invoice — Billix" }] }),
  component: NewInvoicePage,
});

interface CustomerListResponse {
  items: Customer[];
  total: number;
}

interface ProductListResponse {
  items: Product[];
  total: number;
}

interface FormItemRow {
  tempId: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  discount: number;
  gst_rate: number;
}

function NewInvoicePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { activeBusiness } = useBusiness();

  // 1. Form state variables
  const [customerId, setCustomerId] = useState("");
  const [invoiceDate, setInvoiceDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [dueDate, setDueDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split("T")[0];
  });
  const [overallDiscount, setOverallDiscount] = useState("0");
  const [notes, setNotes] = useState("");
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const [itemRows, setItemRows] = useState<FormItemRow[]>([
    {
      tempId: "row-1",
      product_id: "",
      quantity: 1,
      unit_price: 0,
      discount: 0,
      gst_rate: 0,
    },
  ]);

  // 2. Fetch Customers and Products from backend API
  const { data: customersData, isLoading: isCustLoading } = useBusinessQuery<CustomerListResponse>(
    ["customers", "dropdown"],
    "/api/v1/customers?limit=100",
  );
  const { data: productsData, isLoading: isProdLoading } = useBusinessQuery<ProductListResponse>(
    ["products", "dropdown"],
    "/api/v1/products?limit=100",
  );

  const productMap = new Map((productsData?.items || []).map((p) => [p.id, p]));
  const selectedCustomer = (customersData?.items || []).find((c) => c.id === customerId);

  // 3. Create Invoice Mutation
  const createInvoiceMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => {
      return apiClient<Invoice>("/api/v1/invoices", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: (res) => {
      invalidateCache("invoice:create", queryClient);
      toast.success("Invoice generated successfully.");
      navigate({ to: "/invoices/$id", params: { id: res.id } });
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create invoice.");
    },
  });

  // 4. Calculations preview matching backend InvoiceCalculator
  const parsedOverallDiscount = parseFloat(overallDiscount) || 0;

  const calculatedRows = itemRows.map((r) => {
    const qty = r.quantity > 0 ? r.quantity : 0;
    const price = r.unit_price >= 0 ? r.unit_price : 0;
    const disc = r.discount >= 0 ? r.discount : 0;
    const rate = r.gst_rate >= 0 ? r.gst_rate : 0;

    const lineTotal = qty * price;
    const taxable = Math.max(0, lineTotal - disc);
    const tax = (taxable * rate) / 100;
    const total = taxable + tax;

    return { ...r, lineTotal, taxable, tax, total };
  });

  const subtotal = calculatedRows.reduce((sum, r) => sum + r.lineTotal, 0);
  const totalItemDiscounts = calculatedRows.reduce((sum, r) => sum + r.discount, 0);
  const totalTax = calculatedRows.reduce((sum, r) => sum + r.tax, 0);

  const taxableAmount = Math.max(0, subtotal - totalItemDiscounts - parsedOverallDiscount);
  const totalBeforeRound = taxableAmount + totalTax;
  const grandTotal = Math.round(totalBeforeRound);
  const roundOff = grandTotal - totalBeforeRound;

  // Determine GST Split (Intra-state CGST/SGST vs Inter-state IGST)
  const isSameState =
    !selectedCustomer?.state ||
    !activeBusiness?.state ||
    selectedCustomer.state.trim().toLowerCase() === activeBusiness.state.trim().toLowerCase();

  const cgst = isSameState ? totalTax / 2 : 0;
  const sgst = isSameState ? totalTax / 2 : 0;
  const igst = !isSameState ? totalTax : 0;

  // Row handlers
  const handleProductSelect = (index: number, prodId: string) => {
    const prod = productMap.get(prodId);
    const updated = [...itemRows];
    updated[index] = {
      ...updated[index],
      product_id: prodId,
      unit_price: prod?.selling_price || prod?.purchase_price || 0,
      gst_rate: prod?.gst_rate || 0,
    };
    setItemRows(updated);
  };

  const handleRowChange = (index: number, field: keyof FormItemRow, val: number) => {
    const updated = [...itemRows];
    updated[index] = {
      ...updated[index],
      [field]: val,
    };
    setItemRows(updated);
  };

  const handleAddRow = () => {
    setItemRows([
      ...itemRows,
      {
        tempId: `row-${Date.now()}`,
        product_id: "",
        quantity: 1,
        unit_price: 0,
        discount: 0,
        gst_rate: 0,
      },
    ]);
  };

  const handleRemoveRow = (index: number) => {
    if (itemRows.length <= 1) {
      toast.error("An invoice must contain at least one item line.");
      return;
    }
    const updated = itemRows.filter((_, i) => i !== index);
    setItemRows(updated);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!customerId) {
      errors.customer_id = "Please select a customer for this invoice.";
    }

    const invalidItems = itemRows.some((r) => !r.product_id || r.quantity <= 0 || r.unit_price < 0);
    if (invalidItems) {
      errors.items =
        "All rows must have a selected product, quantity > 0, and non-negative unit price.";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
      customer_id: customerId,
      invoice_date: new Date(invoiceDate).toISOString(),
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
      discount_amount: parsedOverallDiscount > 0 ? parsedOverallDiscount : null,
      notes: notes.trim() || null,
      items: itemRows.map((r) => ({
        product_id: r.product_id,
        quantity: r.quantity,
        unit_price: r.unit_price,
        discount: r.discount > 0 ? r.discount : null,
        gst_rate: r.gst_rate > 0 ? r.gst_rate : null,
      })),
    };

    createInvoiceMutation.mutate(payload);
  };

  return (
    <AppShell>
      <form onSubmit={handleSubmit}>
        <PageHeader
          title="Create Tax Invoice"
          description="Raise a GST-compliant tax invoice with automatic inventory integration."
          actions={
            <>
              <Button asChild variant="ghost" size="sm">
                <Link to="/invoices">
                  <ArrowLeft className="h-4 w-4 mr-1" /> Cancel
                </Link>
              </Button>
              <Button
                type="submit"
                size="sm"
                disabled={createInvoiceMutation.isPending}
                className="gap-1.5 shadow-sm"
              >
                <Send className="h-4 w-4" /> Issue Invoice
              </Button>
            </>
          }
        />

        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <div className="space-y-6">
            <Card className="shadow-sm border">
              <CardHeader>
                <CardTitle className="text-base font-bold">Customer & Billing Details</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1 sm:col-span-2">
                  <Label htmlFor="customer_id">Select Customer *</Label>
                  <select
                    id="customer_id"
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                    value={customerId}
                    onChange={(e) => setCustomerId(e.target.value)}
                  >
                    <option value="">-- Choose Customer Profile --</option>
                    {(customersData?.items || []).map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} {c.gstin ? `(GSTIN: ${c.gstin})` : ""}
                      </option>
                    ))}
                  </select>
                  {formErrors.customer_id && (
                    <p className="text-xs text-destructive">{formErrors.customer_id}</p>
                  )}
                </div>

                <div className="space-y-1">
                  <Label htmlFor="invoice_date">Invoice Date *</Label>
                  <Input
                    id="invoice_date"
                    type="date"
                    value={invoiceDate}
                    onChange={(e) => setInvoiceDate(e.target.value)}
                  />
                </div>

                <div className="space-y-1">
                  <Label htmlFor="due_date">Due Date</Label>
                  <Input
                    id="due_date"
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <Label>Place of Supply</Label>
                  <div className="text-xs text-muted-foreground p-2 rounded border bg-muted/30">
                    {selectedCustomer
                      ? `Billing State: ${selectedCustomer.state || "Not specified"} (${
                          isSameState ? "Intra-State: CGST + SGST" : "Inter-State: IGST"
                        })`
                      : "Select a customer to determine place of supply"}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm border">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-base font-bold">Line Items</CardTitle>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="gap-1.5"
                  onClick={handleAddRow}
                >
                  <Plus className="h-4 w-4" /> Add Row
                </Button>
              </CardHeader>
              <CardContent className="p-0">
                {formErrors.items && (
                  <div className="p-3 text-xs text-destructive font-medium border-b bg-destructive/5">
                    {formErrors.items}
                  </div>
                )}
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="min-w-[220px]">Product Item *</TableHead>
                        <TableHead className="text-right w-24">Qty *</TableHead>
                        <TableHead className="text-right w-28">Rate (₹)</TableHead>
                        <TableHead className="text-right w-24">Discount (₹)</TableHead>
                        <TableHead className="text-right w-24">GST %</TableHead>
                        <TableHead className="text-right w-28">Total (₹)</TableHead>
                        <TableHead className="w-10" />
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {itemRows.map((r, index) => {
                        const calculated = calculatedRows[index];

                        return (
                          <TableRow key={r.tempId}>
                            <TableCell>
                              <select
                                className="flex h-9 w-full rounded-md border border-input bg-transparent px-2 py-1 text-xs shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                                value={r.product_id}
                                onChange={(e) => handleProductSelect(index, e.target.value)}
                              >
                                <option value="">-- Select Product --</option>
                                {(productsData?.items || []).map((p) => (
                                  <option key={p.id} value={p.id}>
                                    {p.name} (Stock: {p.current_stock})
                                  </option>
                                ))}
                              </select>
                            </TableCell>
                            <TableCell className="text-right">
                              <Input
                                type="number"
                                step="any"
                                min={1}
                                className="h-8 w-20 text-right ml-auto text-xs"
                                value={r.quantity}
                                onChange={(e) =>
                                  handleRowChange(
                                    index,
                                    "quantity",
                                    parseFloat(e.target.value) || 0,
                                  )
                                }
                              />
                            </TableCell>
                            <TableCell className="text-right">
                              <Input
                                type="number"
                                step="any"
                                min={0}
                                className="h-8 w-24 text-right ml-auto text-xs"
                                value={r.unit_price}
                                onChange={(e) =>
                                  handleRowChange(
                                    index,
                                    "unit_price",
                                    parseFloat(e.target.value) || 0,
                                  )
                                }
                              />
                            </TableCell>
                            <TableCell className="text-right">
                              <Input
                                type="number"
                                step="any"
                                min={0}
                                className="h-8 w-20 text-right ml-auto text-xs"
                                value={r.discount}
                                onChange={(e) =>
                                  handleRowChange(
                                    index,
                                    "discount",
                                    parseFloat(e.target.value) || 0,
                                  )
                                }
                              />
                            </TableCell>
                            <TableCell className="text-right">
                              <Input
                                type="number"
                                step="any"
                                min={0}
                                max={100}
                                className="h-8 w-20 text-right ml-auto text-xs"
                                value={r.gst_rate}
                                onChange={(e) =>
                                  handleRowChange(
                                    index,
                                    "gst_rate",
                                    parseFloat(e.target.value) || 0,
                                  )
                                }
                              />
                            </TableCell>
                            <TableCell className="text-right font-bold text-xs">
                              ₹
                              {calculated.total.toLocaleString("en-IN", {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </TableCell>
                            <TableCell>
                              <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-destructive hover:bg-destructive/10 cursor-pointer"
                                onClick={() => handleRemoveRow(index)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm border">
              <CardHeader>
                <CardTitle className="text-base font-bold">Invoice Remarks & Terms</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1">
                  <Label htmlFor="notes">Notes to Customer</Label>
                  <Textarea
                    id="notes"
                    rows={3}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Thank you for your business! Payment due within terms."
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="shadow-sm border">
              <CardHeader>
                <CardTitle className="text-base font-bold">Calculation Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <SummaryRow
                  label="Subtotal"
                  value={`₹${subtotal.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />

                <div className="space-y-1">
                  <Label htmlFor="overall_discount" className="text-xs">
                    Overall Invoice Discount (₹)
                  </Label>
                  <Input
                    id="overall_discount"
                    type="number"
                    step="any"
                    value={overallDiscount}
                    onChange={(e) => setOverallDiscount(e.target.value)}
                    placeholder="0"
                    className="h-8 text-xs"
                  />
                </div>

                <SummaryRow
                  label="Taxable Amount"
                  value={`₹${taxableAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />

                {isSameState ? (
                  <>
                    <SummaryRow
                      label="CGST"
                      value={`₹${cgst.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                    />
                    <SummaryRow
                      label="SGST"
                      value={`₹${sgst.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                    />
                  </>
                ) : (
                  <SummaryRow
                    label="IGST"
                    value={`₹${igst.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                  />
                )}

                <SummaryRow label="Round Off" value={`₹${roundOff.toFixed(2)}`} />

                <Separator />
                <div className="flex items-center justify-between font-display text-lg font-bold text-foreground">
                  <span>Grand Total</span>
                  <span>
                    ₹
                    {grandTotal.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </AppShell>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold text-foreground">{value}</span>
    </div>
  );
}
