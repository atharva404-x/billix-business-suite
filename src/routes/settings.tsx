import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { useBusiness } from "@/hooks/use-business";
import { useUser } from "@clerk/tanstack-react-start";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Settings — Billix" }] }),
  component: SettingsPage,
});

function SettingsPage() {
  const { activeBusiness, updateBusiness } = useBusiness();
  const { user } = useUser();

  const [businessName, setBusinessName] = useState("");
  const [legalName, setLegalName] = useState("");
  const [gstin, setGstin] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (activeBusiness) {
      setBusinessName(activeBusiness.business_name || "");
      setLegalName(activeBusiness.legal_name || activeBusiness.business_name || "");
      setGstin(activeBusiness.gstin || "");
      setAddress(activeBusiness.address_line1 || "");
      setCity(activeBusiness.city || "");
      setState(activeBusiness.state || "");
      setPincode(activeBusiness.pincode || "");
    }
  }, [activeBusiness]);

  const handleSaveBusiness = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeBusiness) {
      toast.error("No active business selected");
      return;
    }
    setIsSaving(true);
    try {
      await updateBusiness(activeBusiness.id, {
        business_name: businessName,
        legal_name: legalName,
        gstin,
        address_line1: address,
        city,
        state,
        pincode,
      });
      toast.success("Business settings saved successfully");
    } catch (err: unknown) {
      const error = err as Error;
      toast.error(error.message || "Failed to save business settings");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      <PageHeader
        title="Settings"
        description="Configure your workspace, invoicing rules and team preferences."
      />
      <Tabs defaultValue="business" className="space-y-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="business">Business</TabsTrigger>
          <TabsTrigger value="invoice">Invoice</TabsTrigger>
          <TabsTrigger value="tax">Tax & GST</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        <TabsContent value="business">
          <Card>
            <CardHeader>
              <CardTitle>Business details</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveBusiness} className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="tradeName">Trade / Display Name</Label>
                  <Input
                    id="tradeName"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    placeholder="Business Name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="legalName">Legal Entity Name</Label>
                  <Input
                    id="legalName"
                    value={legalName}
                    onChange={(e) => setLegalName(e.target.value)}
                    placeholder="Legal Name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gstin">GSTIN</Label>
                  <Input
                    id="gstin"
                    value={gstin}
                    onChange={(e) => setGstin(e.target.value)}
                    placeholder="27ABCDE1234F1Z5"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="Street Address"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="City"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State</Label>
                  <Input
                    id="state"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="State"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="pincode">Pincode</Label>
                  <Input
                    id="pincode"
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value)}
                    placeholder="Pincode"
                  />
                </div>
                <div className="sm:col-span-2 mt-2">
                  <Button type="submit" disabled={isSaving}>
                    {isSaving ? "Saving changes..." : "Save changes"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="invoice">
          <Card>
            <CardHeader>
              <CardTitle>Invoice preferences</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Field label="Invoice prefix" defaultValue="INV-" />
              <Field label="Next number" defaultValue="1001" />
              <div className="space-y-2">
                <Label>Currency</Label>
                <Select defaultValue="inr">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="inr">₹ Indian Rupee (INR)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Default template</Label>
                <Select defaultValue="tax">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tax">Tax Invoice</SelectItem>
                    <SelectItem value="retail">Retail (Thermal)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Toggle label="Show HSN / SAC on invoice" defaultChecked />
              <Toggle label="Round off totals" defaultChecked />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tax">
          <Card>
            <CardHeader>
              <CardTitle>Tax & GST</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Field label="Default GST rate" defaultValue="18%" />
              <Toggle label="Include tax in prices" />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="team">
          <Card>
            <CardHeader>
              <CardTitle>Team members</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-medium">
                    {user?.fullName || user?.primaryEmailAddress?.emailAddress || "Workspace Owner"}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {user?.primaryEmailAddress?.emailAddress || "Primary Owner"}
                  </div>
                </div>
                <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                  Owner
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Toggle label="Email invoice receipts" defaultChecked />
              <Toggle label="Payment received alerts" defaultChecked />
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
