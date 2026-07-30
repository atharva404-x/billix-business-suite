import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Building2, Plus, Check } from "lucide-react";
import { useBusiness } from "@/hooks/use-business";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/common/status-badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export const Route = createFileRoute("/business-profiles")({
  head: () => ({ meta: [{ title: "Business Profiles — Billix" }] }),
  component: BusinessProfilesPage,
});

function BusinessProfilesPage() {
  const { businesses, activeBusinessId, switchBusiness, createBusiness, isLoading } = useBusiness();
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [gstin, setGstin] = useState("");
  const [city, setCity] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Business Name is required");
      return;
    }
    setSubmitting(true);
    try {
      await createBusiness({
        business_name: name,
        gstin: gstin.trim() || undefined,
        city: city.trim() || undefined,
      });
      toast.success("Business profile created successfully");
      setOpen(false);
      setName("");
      setGstin("");
      setCity("");
    } catch (err: unknown) {
      const error = err as Error;
      toast.error(error.message || "Failed to create business profile");
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <AppShell>
        <PageHeader
          title="Business Profiles"
          description="Manage multiple GSTINs, branches and outlets."
        />
        <div className="flex h-40 items-center justify-center text-sm text-muted-foreground animate-pulse">
          Loading business profiles...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <PageHeader
        title="Business Profiles"
        description="Manage multiple GSTINs, branches and outlets from one login."
        actions={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="gap-1.5">
                <Plus className="h-4 w-4" /> Add Business
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add Business Profile</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4 pt-2">
                <div className="space-y-2">
                  <Label htmlFor="b-name">Business Name *</Label>
                  <Input
                    id="b-name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Retail Store"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="b-gstin">GSTIN (Optional)</Label>
                  <Input
                    id="b-gstin"
                    value={gstin}
                    onChange={(e) => setGstin(e.target.value.toUpperCase())}
                    placeholder="27ABCDE1234F1Z5"
                    maxLength={15}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="b-city">City (Optional)</Label>
                  <Input
                    id="b-city"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="e.g. Mumbai"
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={submitting}>
                    {submitting ? "Creating..." : "Create Business"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        }
      />
      <div className="grid gap-4 md:grid-cols-2">
        {businesses.map((b) => {
          const isActive = b.id === activeBusinessId;
          return (
            <Card
              key={b.id}
              className={`overflow-hidden ${isActive ? "border-primary/50 shadow-sm" : ""}`}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary">
                      <Building2 className="h-6 w-6" />
                    </div>
                    <div className="min-w-0">
                      <div className="font-display text-lg font-semibold">{b.business_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {b.gstin ? `GSTIN ${b.gstin}` : "No GSTIN"} {b.city ? `· ${b.city}` : ""}
                      </div>
                    </div>
                  </div>
                  <StatusBadge status={isActive ? "Active" : "Inactive"} />
                </div>
                <div className="mt-6 flex items-center gap-2">
                  {isActive ? (
                    <Button size="sm" variant="secondary" className="gap-1.5" disabled>
                      <Check className="h-4 w-4" /> Current
                    </Button>
                  ) : (
                    <Button size="sm" onClick={() => switchBusiness(b.id)}>
                      Switch to this
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      switchBusiness(b.id);
                      navigate({ to: "/settings" });
                    }}
                  >
                    Edit Settings
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </AppShell>
  );
}
