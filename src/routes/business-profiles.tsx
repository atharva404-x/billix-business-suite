import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Building2, Plus, Check, Trash2, Edit3 } from "lucide-react";
import { useBusiness, BusinessProfile } from "@/hooks/use-business";
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export const Route = createFileRoute("/business-profiles")({
  head: () => ({ meta: [{ title: "Business Profiles — Billix" }] }),
  component: BusinessProfilesPage,
});

function BusinessProfilesPage() {
  const {
    businesses,
    activeBusinessId,
    switchBusiness,
    createBusiness,
    updateBusiness,
    deleteBusiness,
    isLoading,
  } = useBusiness();
  const navigate = useNavigate();

  const [createOpen, setCreateOpen] = useState(false);
  const [name, setName] = useState("");
  const [gstin, setGstin] = useState("");
  const [city, setCity] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Edit Business Dialog state
  const [editingBusiness, setEditingBusiness] = useState<BusinessProfile | null>(null);
  const [editName, setEditName] = useState("");
  const [editGstin, setEditGstin] = useState("");
  const [editAddress, setEditAddress] = useState("");
  const [editCity, setEditCity] = useState("");
  const [editState, setEditState] = useState("");
  const [editPincode, setEditPincode] = useState("");

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
      setCreateOpen(false);
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

  const handleOpenEdit = (b: BusinessProfile) => {
    setEditingBusiness(b);
    setEditName(b.business_name || "");
    setEditGstin(b.gstin || "");
    setEditAddress(b.address || b.address_line1 || "");
    setEditCity(b.city || "");
    setEditState(b.state || "");
    setEditPincode(b.pincode || "");
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingBusiness) return;
    if (!editName.trim()) {
      toast.error("Business Name is required");
      return;
    }
    setSubmitting(true);
    try {
      await updateBusiness(editingBusiness.id, {
        business_name: editName,
        gstin: editGstin.trim() || undefined,
        address: editAddress.trim() || undefined,
        city: editCity.trim() || undefined,
        state: editState.trim() || undefined,
        pincode: editPincode.trim() || undefined,
      });
      toast.success("Business profile updated successfully");
      setEditingBusiness(null);
    } catch (err: unknown) {
      const error = err as Error;
      toast.error(error.message || "Failed to update business profile");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteBusiness(id);
    } catch (err: unknown) {
      // Error toast already displayed inside hook
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
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
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
                  <Button type="button" variant="outline" onClick={() => setCreateOpen(false)}>
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
                      <div className="text-xs text-muted-foreground mt-0.5">
                        {b.gstin ? `GSTIN ${b.gstin}` : "No GSTIN registered"}{" "}
                        {b.city ? `· ${b.city}` : ""}
                      </div>
                      {b.address && (
                        <div className="text-xs text-muted-foreground truncate mt-1">
                          {b.address}
                        </div>
                      )}
                    </div>
                  </div>
                  <StatusBadge status={isActive ? "Active" : "Inactive"} />
                </div>
                <div className="mt-6 flex items-center justify-between gap-2 border-t pt-4">
                  <div className="flex items-center gap-2">
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
                      className="gap-1.5"
                      onClick={() => handleOpenEdit(b)}
                    >
                      <Edit3 className="h-3.5 w-3.5" /> Edit
                    </Button>
                  </div>

                  {!isActive && businesses.length > 1 && (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Business Profile?</AlertDialogTitle>
                          <AlertDialogDescription>
                            Are you sure you want to delete &quot;{b.business_name}&quot;? Profiles
                            with active invoices or records cannot be deleted.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            onClick={() => handleDelete(b.id)}
                          >
                            Delete Profile
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Edit Business Profile Dialog */}
      <Dialog open={!!editingBusiness} onOpenChange={(open) => !open && setEditingBusiness(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Business Profile</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSaveEdit} className="space-y-4 pt-2">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Business Name *</Label>
              <Input
                id="edit-name"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="edit-gstin">GSTIN</Label>
                <Input
                  id="edit-gstin"
                  value={editGstin}
                  onChange={(e) => setEditGstin(e.target.value.toUpperCase())}
                  maxLength={15}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-city">City</Label>
                <Input
                  id="edit-city"
                  value={editCity}
                  onChange={(e) => setEditCity(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-address">Address</Label>
              <Input
                id="edit-address"
                value={editAddress}
                onChange={(e) => setEditAddress(e.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="edit-state">State</Label>
                <Input
                  id="edit-state"
                  value={editState}
                  onChange={(e) => setEditState(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-pincode">Pincode</Label>
                <Input
                  id="edit-pincode"
                  value={editPincode}
                  onChange={(e) => setEditPincode(e.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => setEditingBusiness(null)}>
                Cancel
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
