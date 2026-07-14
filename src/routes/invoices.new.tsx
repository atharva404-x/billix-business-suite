import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, Trash2, Save, Send } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";

export const Route = createFileRoute("/invoices/new")({
  head: () => ({ meta: [{ title: "New Invoice — Billix" }] }),
  component: NewInvoicePage,
});

const rows = [
  { name: "Paracetamol 500mg", qty: 10, price: 18, gst: 12 },
  { name: "Cotton T-Shirt (M)", qty: 2, price: 399, gst: 5 },
];

function NewInvoicePage() {
  const subtotal = rows.reduce((s, r) => s + r.qty * r.price, 0);
  const gst = rows.reduce((s, r) => s + (r.qty * r.price * r.gst) / 100, 0);
  const total = subtotal + gst;
  return (
    <AppShell>
      <PageHeader
        title="Create Invoice"
        description="Raise a GST-compliant tax invoice in seconds."
        actions={
          <>
            <Button asChild variant="ghost" size="sm"><Link to="/invoices">Cancel</Link></Button>
            <Button variant="outline" size="sm" className="gap-1.5"><Save className="h-4 w-4" /> Save draft</Button>
            <Button size="sm" className="gap-1.5"><Send className="h-4 w-4" /> Save & Send</Button>
          </>
        }
      />
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Bill to</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2 sm:col-span-2">
                <Label>Customer</Label>
                <Select>
                  <SelectTrigger><SelectValue placeholder="Search or add customer" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Sharma Traders</SelectItem>
                    <SelectItem value="2">Raj Medical Store</SelectItem>
                    <SelectItem value="3">Krishna Hardware</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2"><Label>Invoice #</Label><Input defaultValue="INV-2042" /></div>
              <div className="space-y-2"><Label>Date</Label><Input type="date" defaultValue="2026-07-14" /></div>
              <div className="space-y-2"><Label>Place of supply</Label><Input defaultValue="Maharashtra (27)" /></div>
              <div className="space-y-2"><Label>Due date</Label><Input type="date" defaultValue="2026-07-28" /></div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Items</CardTitle>
              <Button size="sm" variant="outline" className="gap-1.5"><Plus className="h-4 w-4" /> Add Item</Button>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="min-w-[220px]">Item</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead className="text-right">Rate</TableHead>
                      <TableHead className="text-right">GST%</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead className="w-10" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rows.map((r) => (
                      <TableRow key={r.name}>
                        <TableCell><div className="font-medium">{r.name}</div><div className="text-xs text-muted-foreground">HSN 3004 · Strip</div></TableCell>
                        <TableCell className="text-right"><Input defaultValue={r.qty} className="ml-auto h-8 w-16 text-right" /></TableCell>
                        <TableCell className="text-right"><Input defaultValue={r.price} className="ml-auto h-8 w-20 text-right" /></TableCell>
                        <TableCell className="text-right">{r.gst}%</TableCell>
                        <TableCell className="text-right font-semibold">₹{(r.qty * r.price).toLocaleString("en-IN")}</TableCell>
                        <TableCell><Button variant="ghost" size="icon" className="h-8 w-8 text-destructive"><Trash2 className="h-4 w-4" /></Button></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Notes & Terms</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2"><Label>Notes to customer</Label><Textarea placeholder="Thank you for your business!" /></div>
              <div className="space-y-2"><Label>Terms & conditions</Label><Textarea placeholder="Payment due within 14 days." /></div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
            <CardContent className="space-y-3 text-sm">
              <Row label="Subtotal" value={`₹${subtotal.toLocaleString("en-IN")}`} />
              <Row label="CGST" value={`₹${(gst / 2).toFixed(2)}`} />
              <Row label="SGST" value={`₹${(gst / 2).toFixed(2)}`} />
              <Row label="Round off" value="₹0.00" />
              <Separator />
              <div className="flex items-center justify-between font-display text-lg font-bold">
                <span>Total</span><span>₹{total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</span>
              </div>
              <div className="rounded-lg bg-muted/60 p-3 text-xs text-muted-foreground">
                Amount in words: Rupees {Math.round(total)} only
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Payment</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <Label>Mode</Label>
                <Select>
                  <SelectTrigger><SelectValue placeholder="Select mode" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cash">Cash</SelectItem>
                    <SelectItem value="upi">UPI</SelectItem>
                    <SelectItem value="card">Card</SelectItem>
                    <SelectItem value="bank">Bank Transfer</SelectItem>
                    <SelectItem value="credit">On Credit</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2"><Label>Reference</Label><Input placeholder="UTR / txn id" /></div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}