import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Settings — Billix" }] }),
  component: SettingsPage,
});

function SettingsPage() {
  return (
    <AppShell>
      <PageHeader title="Settings" description="Configure your workspace, invoicing rules and integrations." />
      <Tabs defaultValue="business" className="space-y-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="business">Business</TabsTrigger>
          <TabsTrigger value="invoice">Invoice</TabsTrigger>
          <TabsTrigger value="tax">Tax & GST</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="billing">Plan & Billing</TabsTrigger>
        </TabsList>

        <TabsContent value="business">
          <Card>
            <CardHeader><CardTitle>Business details</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Field label="Legal name" defaultValue="Sharma Retail Store" />
              <Field label="Trade name" defaultValue="Sharma Retail" />
              <Field label="GSTIN" defaultValue="27ABCDE1234F1Z5" />
              <Field label="PAN" defaultValue="ABCDE1234F" />
              <Field label="Address" defaultValue="14 Market Rd, Andheri West" />
              <Field label="City" defaultValue="Mumbai" />
              <Field label="State" defaultValue="Maharashtra" />
              <Field label="Pincode" defaultValue="400058" />
              <div className="sm:col-span-2"><Button>Save changes</Button></div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="invoice">
          <Card>
            <CardHeader><CardTitle>Invoice preferences</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Field label="Invoice prefix" defaultValue="INV-" />
              <Field label="Next number" defaultValue="2042" />
              <div className="space-y-2"><Label>Currency</Label>
                <Select defaultValue="inr"><SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="inr">₹ Indian Rupee</SelectItem></SelectContent>
                </Select>
              </div>
              <div className="space-y-2"><Label>Default template</Label>
                <Select defaultValue="tax"><SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tax">Tax Invoice</SelectItem>
                    <SelectItem value="retail">Retail (Thermal)</SelectItem>
                    <SelectItem value="proforma">Proforma</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Toggle label="Show HSN / SAC on invoice" defaultChecked />
              <Toggle label="Enable e-invoice (IRN)" defaultChecked />
              <Toggle label="Enable e-way bill" />
              <Toggle label="Round off totals" defaultChecked />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tax">
          <Card>
            <CardHeader><CardTitle>Tax & GST</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Field label="Default GST rate" defaultValue="18%" />
              <Field label="Composition scheme" defaultValue="No" />
              <Toggle label="Reverse charge applicable" />
              <Toggle label="Include TCS in invoice" />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="team">
          <Card>
            <CardHeader><CardTitle>Team members</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {[
                { n: "Rahul Sharma", r: "Owner", e: "rahul@sharmaretail.in" },
                { n: "Priya Nair", r: "Cashier", e: "priya@sharmaretail.in" },
                { n: "Ankit Verma", r: "Accountant", e: "ankit@sharmaretail.in" },
              ].map((t) => (
                <div key={t.e} className="flex items-center justify-between rounded-lg border p-3">
                  <div><div className="font-medium">{t.n}</div><div className="text-xs text-muted-foreground">{t.e}</div></div>
                  <div className="flex items-center gap-2"><span className="rounded-full bg-muted px-2 py-0.5 text-xs">{t.r}</span><Button size="sm" variant="outline">Manage</Button></div>
                </div>
              ))}
              <Separator />
              <Button>Invite member</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader><CardTitle>Notifications</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Toggle label="Email invoice receipts" defaultChecked />
              <Toggle label="Payment received alerts" defaultChecked />
              <Toggle label="Low stock alerts" defaultChecked />
              <Toggle label="Weekly summary email" />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing">
          <Card>
            <CardHeader><CardTitle>Plan & Billing</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-xl border bg-gradient-to-br from-primary/10 to-accent/40 p-5">
                <div className="text-xs uppercase text-muted-foreground">Current plan</div>
                <div className="mt-1 font-display text-2xl font-bold">Billix Growth · ₹999/mo</div>
                <div className="mt-1 text-xs text-muted-foreground">Renews on 03 Aug 2026</div>
                <div className="mt-4 flex gap-2"><Button>Upgrade plan</Button><Button variant="outline">Manage billing</Button></div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}

function Field({ label, defaultValue }: { label: string; defaultValue?: string }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Input defaultValue={defaultValue} />
    </div>
  );
}

function Toggle({ label, defaultChecked }: { label: string; defaultChecked?: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-3">
      <div className="text-sm font-medium">{label}</div>
      <Switch defaultChecked={defaultChecked} />
    </div>
  );
}