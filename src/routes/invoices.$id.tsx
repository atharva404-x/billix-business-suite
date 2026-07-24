import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, Printer, Download, Send, Copy } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { StatusBadge } from "@/components/common/status-badge";

export const Route = createFileRoute("/invoices/$id")({
  head: () => ({ meta: [{ title: "Invoice — Billix" }] }),
  component: InvoiceDetails,
});

function InvoiceDetails() {
  const { id } = Route.useParams();
  const items = [
    { name: "Paracetamol 500mg", hsn: "3004", qty: 10, rate: 18, gst: 12 },
    { name: "Cotton T-Shirt (M)", hsn: "6109", qty: 2, rate: 399, gst: 5 },
  ];
  const subtotal = items.reduce((s, i) => s + i.qty * i.rate, 0);
  const gst = items.reduce((s, i) => s + (i.qty * i.rate * i.gst) / 100, 0);
  const total = subtotal + gst;

  return (
    <AppShell>
      <PageHeader
        title={`Invoice ${id}`}
        description="Tax invoice · Original for Recipient"
        actions={
          <>
            <Button asChild variant="ghost" size="sm" className="gap-1.5">
              <Link to="/invoices">
                <ArrowLeft className="h-4 w-4" /> Back
              </Link>
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Copy className="h-4 w-4" /> Duplicate
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Printer className="h-4 w-4" /> Print
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Download className="h-4 w-4" /> PDF
            </Button>
            <Button size="sm" className="gap-1.5">
              <Send className="h-4 w-4" /> Send
            </Button>
          </>
        }
      />
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardContent className="p-8">
            <div className="flex flex-col justify-between gap-6 sm:flex-row">
              <div>
                <div className="font-display text-2xl font-bold">Sharma Retail Store</div>
                <div className="mt-1 text-xs text-muted-foreground">GSTIN: 27ABCDE1234F1Z5</div>
                <div className="text-xs text-muted-foreground">
                  14 Market Rd, Andheri West, Mumbai 400058
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs uppercase text-muted-foreground">Tax Invoice</div>
                <div className="font-display text-xl font-bold">{id}</div>
                <div className="mt-1 text-xs text-muted-foreground">Date: 12 Jul 2026</div>
                <div className="mt-2">
                  <StatusBadge status="Paid" />
                </div>
              </div>
            </div>
            <Separator className="my-6" />
            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <div className="text-xs uppercase text-muted-foreground">Bill to</div>
                <div className="mt-1 font-semibold">Sharma Traders</div>
                <div className="text-xs text-muted-foreground">GSTIN 27ABCDE1234F1Z5</div>
                <div className="text-xs text-muted-foreground">MG Road, Mumbai 400001</div>
              </div>
              <div className="sm:text-right">
                <div className="text-xs uppercase text-muted-foreground">Place of supply</div>
                <div className="mt-1 font-semibold">Maharashtra (27)</div>
                <div className="mt-2 text-xs uppercase text-muted-foreground">Due date</div>
                <div className="font-semibold">28 Jul 2026</div>
              </div>
            </div>
            <div className="mt-8 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b text-left text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="py-2">Item</th>
                    <th>HSN</th>
                    <th className="text-right">Qty</th>
                    <th className="text-right">Rate</th>
                    <th className="text-right">GST</th>
                    <th className="text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((i) => (
                    <tr key={i.name} className="border-b last:border-0">
                      <td className="py-3 font-medium">{i.name}</td>
                      <td className="text-xs text-muted-foreground">{i.hsn}</td>
                      <td className="text-right">{i.qty}</td>
                      <td className="text-right">₹{i.rate}</td>
                      <td className="text-right">{i.gst}%</td>
                      <td className="text-right font-semibold">
                        ₹{(i.qty * i.rate).toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-6 flex justify-end">
              <div className="w-full max-w-xs space-y-2 text-sm">
                <Row l="Subtotal" v={`₹${subtotal.toLocaleString("en-IN")}`} />
                <Row l="CGST" v={`₹${(gst / 2).toFixed(2)}`} />
                <Row l="SGST" v={`₹${(gst / 2).toFixed(2)}`} />
                <Separator />
                <div className="flex items-center justify-between font-display text-lg font-bold">
                  <span>Total</span>
                  <span>₹{total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <div className="space-y-6">
          <Card>
            <CardContent className="p-5">
              <div className="text-xs uppercase text-muted-foreground">Payment</div>
              <div className="mt-2 font-display text-2xl font-bold">₹{total.toFixed(2)}</div>
              <div className="text-xs text-muted-foreground">Received via UPI · 12 Jul 2026</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-5">
              <div className="text-xs uppercase text-muted-foreground">Timeline</div>
              <ul className="mt-3 space-y-3 text-sm">
                <li className="flex gap-3">
                  <Dot color="bg-success" />
                  <div>
                    <div className="font-medium">Payment received</div>
                    <div className="text-xs text-muted-foreground">12 Jul, 4:12 PM</div>
                  </div>
                </li>
                <li className="flex gap-3">
                  <Dot color="bg-primary" />
                  <div>
                    <div className="font-medium">Invoice sent</div>
                    <div className="text-xs text-muted-foreground">12 Jul, 11:03 AM</div>
                  </div>
                </li>
                <li className="flex gap-3">
                  <Dot color="bg-muted-foreground" />
                  <div>
                    <div className="font-medium">Invoice created</div>
                    <div className="text-xs text-muted-foreground">12 Jul, 10:58 AM</div>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function Row({ l, v }: { l: string; v: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{l}</span>
      <span className="font-medium">{v}</span>
    </div>
  );
}
function Dot({ color }: { color: string }) {
  return <span className={`mt-1.5 inline-block h-2 w-2 shrink-0 rounded-full ${color}`} />;
}
