import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
import {
  Plus,
  MoreHorizontal,
  Truck,
  Search,
  SlidersHorizontal,
  Download,
  Trash2,
  Edit,
  Eye,
  ArrowUpDown,
  Mail,
  Phone,
  MapPin,
  Building2,
  UserCheck,
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
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { KpiCard } from "@/components/common/kpi-card";
import { StatusBadge } from "@/components/common/status-badge";
import { SimplePagination } from "@/components/common/simple-pagination";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

export const Route = createFileRoute("/suppliers")({
  head: () => ({ meta: [{ title: "Suppliers — Billix" }] }),
  component: SuppliersPage,
});

export interface Supplier {
  id: string;
  business_id: string;
  supplier_code?: string | null;
  name: string;
  type: "INDIVIDUAL" | "BUSINESS";
  gstin?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  pincode?: string | null;
  credit_limit?: number | null;
  outstanding_balance: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

interface SupplierListResponse {
  items: Supplier[];
  total: number;
}

function SuppliersPage() {
  const queryClient = useQueryClient();
  const { activeBusinessId } = useBusiness();

  // 1. Filter and sorting parameters state
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "created_at" | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // 2. Selection and modal states
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [detailSupplier, setDetailSupplier] = useState<Supplier | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | null>(null);

  // 3. Form input states
  const [formData, setFormData] = useState({
    name: "",
    supplier_code: "",
    type: "BUSINESS" as "BUSINESS" | "INDIVIDUAL",
    gstin: "",
    phone: "",
    email: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    credit_limit: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // 4. Debounce input changes
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  // 5. Query Suppliers list from backend API
  const { data, isLoading, error, refetch } = useBusinessQuery<SupplierListResponse>(
    ["suppliers", page, limit, debouncedSearch, sortBy, sortOrder],
    `/api/v1/suppliers?skip=${(page - 1) * limit}&limit=${limit}${
      debouncedSearch ? `&search_query=${encodeURIComponent(debouncedSearch)}` : ""
    }${sortBy ? `&sort_by=${sortBy}&sort_order=${sortOrder}` : ""}`,
  );

  // 6. Mutations
  const createMutation = useMutation({
    mutationFn: (payload: Partial<Supplier>) => {
      return apiClient<Supplier>("/api/v1/suppliers", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("supplier:create", queryClient);
      toast.success("Supplier profile created successfully.");
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create supplier.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (vars: { id: string; payload: Partial<Supplier> }) => {
      return apiClient<Supplier>(`/api/v1/suppliers/${vars.id}`, {
        method: "PATCH",
        body: JSON.stringify(vars.payload),
      });
    },
    onSuccess: () => {
      invalidateCache("supplier:update", queryClient);
      toast.success("Supplier profile updated successfully.");
      setIsDialogOpen(false);
      resetForm();
      if (detailSupplier && detailSupplier.id === selectedSupplier?.id) {
        setIsSheetOpen(false);
        setDetailSupplier(null);
      }
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update supplier.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => {
      return apiClient<Supplier>(`/api/v1/suppliers/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      invalidateCache("supplier:delete", queryClient);
      toast.success("Supplier deactivated successfully.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to deactivate supplier.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      supplier_code: "",
      type: "BUSINESS",
      gstin: "",
      phone: "",
      email: "",
      address: "",
      city: "",
      state: "",
      pincode: "",
      credit_limit: "",
    });
    setFormErrors({});
    setSelectedSupplier(null);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.name.trim()) {
      errors.name = "Supplier name is required.";
    }
    if (formData.gstin.trim() && formData.gstin.trim().length !== 15) {
      errors.gstin = "GSTIN must be exactly 15 characters long.";
    }
    if (formData.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      errors.email = "Please enter a valid email address.";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    const payload: Partial<Supplier> = {
      name: formData.name.trim(),
      supplier_code: formData.supplier_code.trim() || null,
      type: formData.type,
      gstin: formData.gstin.trim().toUpperCase() || null,
      phone: formData.phone.trim() || null,
      email: formData.email.trim() || null,
      address: formData.address.trim() || null,
      city: formData.city.trim() || null,
      state: formData.state.trim() || null,
      pincode: formData.pincode.trim() || null,
      credit_limit: formData.credit_limit ? parseFloat(formData.credit_limit) : null,
    };

    if (selectedSupplier) {
      updateMutation.mutate({ id: selectedSupplier.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleEditClick = (s: Supplier) => {
    setSelectedSupplier(s);
    setFormData({
      name: s.name || "",
      supplier_code: s.supplier_code || "",
      type: s.type || "BUSINESS",
      gstin: s.gstin || "",
      phone: s.phone || "",
      email: s.email || "",
      address: s.address || "",
      city: s.city || "",
      state: s.state || "",
      pincode: s.pincode || "",
      credit_limit:
        s.credit_limit !== undefined && s.credit_limit !== null ? String(s.credit_limit) : "",
    });
    setFormErrors({});
    setIsDialogOpen(true);
  };

  const handleCreateClick = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const handleDeactivateClick = (id: string) => {
    setDeactivatingId(id);
    setIsConfirmOpen(true);
  };

  const handleSort = (field: "name" | "created_at") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const viewDetails = (s: Supplier) => {
    setDetailSupplier(s);
    setIsSheetOpen(true);
  };

  // Render visual skeletons during loader transitions
  if (isLoading) {
    return <SuppliersSkeleton />;
  }

  // Handle server connection error states
  if (error) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load suppliers"
            description={error.message || "Could not retrieve vendor profile entries."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;

  // KPI computations derived directly from backend response
  const totalPayables = items.reduce((sum, s) => sum + (s.outstanding_balance || 0), 0);
  const activeCount = items.filter((s) => s.is_active).length;

  return (
    <AppShell>
      <PageHeader
        title="Suppliers & Vendors"
        description="Manage vendor profiles, GST details, contacts and payables."
        actions={
          <Button onClick={handleCreateClick} className="gap-1.5 shadow-sm">
            <Plus className="h-4 w-4" /> Add Supplier
          </Button>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Total Vendors" value={total.toLocaleString("en-IN")} icon={Truck} />
        <KpiCard
          label="Active Payables"
          value={`₹${totalPayables.toLocaleString("en-IN")}`}
          trend={totalPayables > 0 ? "up" : "down"}
          change={totalPayables > 0 ? "unpaid bills" : "all clear"}
        />
        <KpiCard
          label="Active Supplier Profiles"
          value={activeCount.toLocaleString("en-IN")}
          icon={UserCheck}
        />
      </div>

      <Card className="shadow-sm border">
        <CardContent className="p-4 md:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
            <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search suppliers by name, phone, email or GSTIN…"
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
              <Button variant="outline" size="sm" className="gap-1.5">
                <Download className="h-4 w-4" /> <span className="hidden sm:inline">Export</span>
              </Button>
            </div>
          </div>

          {items.length === 0 ? (
            <EmptyState
              title={search ? "No matching suppliers found" : "No suppliers registered yet"}
              description={
                search
                  ? "Try refining your search keyword or phone number."
                  : "Register your first vendor supplier to manage purchases and payable accounts."
              }
              actionText={search ? undefined : "Add First Supplier"}
              onActionClick={search ? undefined : handleCreateClick}
            />
          ) : (
            <>
              <div className="overflow-x-auto rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-10">
                        <Checkbox
                          checked={items.length > 0 && selectedIds.size === items.length}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedIds(new Set(items.map((s) => s.id)));
                            } else {
                              setSelectedIds(new Set());
                            }
                          }}
                        />
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          onClick={() => handleSort("name")}
                          className="h-8 gap-1 p-0 hover:bg-transparent font-semibold text-xs"
                        >
                          Supplier <ArrowUpDown className="h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>GSTIN</TableHead>
                      <TableHead>Contact Phone / Email</TableHead>
                      <TableHead>City / State</TableHead>
                      <TableHead className="text-right">Outstanding Payable</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-10" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((s) => (
                      <TableRow key={s.id}>
                        <TableCell>
                          <Checkbox
                            checked={selectedIds.has(s.id)}
                            onCheckedChange={(checked) => {
                              const next = new Set(selectedIds);
                              if (checked) next.add(s.id);
                              else next.delete(s.id);
                              setSelectedIds(next);
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <button
                            onClick={() => viewDetails(s)}
                            className="font-semibold text-primary hover:underline text-left block"
                          >
                            {s.name}
                          </button>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            {s.supplier_code || s.type}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {s.gstin || <span className="text-muted-foreground/40">—</span>}
                        </TableCell>
                        <TableCell className="text-xs">
                          <div>
                            {s.phone || <span className="text-muted-foreground/40">—</span>}
                          </div>
                          <div className="text-[10px] text-muted-foreground">{s.email || ""}</div>
                        </TableCell>
                        <TableCell className="text-xs">
                          {s.city || s.state ? (
                            `${s.city || ""}${s.city && s.state ? ", " : ""}${s.state || ""}`
                          ) : (
                            <span className="text-muted-foreground/40">—</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          ₹{(s.outstanding_balance || 0).toLocaleString("en-IN")}
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={s.is_active ? "Active" : "Inactive"} />
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 cursor-pointer"
                              >
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={() => viewDetails(s)}
                              >
                                <Eye className="mr-2 h-4 w-4" /> View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={() => handleEditClick(s)}
                              >
                                <Edit className="mr-2 h-4 w-4" /> Edit Supplier
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="text-destructive focus:text-destructive cursor-pointer"
                                onClick={() => handleDeactivateClick(s.id)}
                              >
                                <Trash2 className="mr-2 h-4 w-4" /> Deactivate
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
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

      {/* CREATE & EDIT SUPPLIER DIALOG */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedSupplier ? "Edit Supplier Profile" : "Register New Supplier"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="sup_name">Supplier / Company Name *</Label>
                <Input
                  id="sup_name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Acme Distributors Ltd"
                />
                {formErrors.name && <p className="text-xs text-destructive">{formErrors.name}</p>}
              </div>

              <div className="space-y-1">
                <Label htmlFor="sup_code">Supplier Code</Label>
                <Input
                  id="sup_code"
                  value={formData.supplier_code}
                  onChange={(e) => setFormData({ ...formData, supplier_code: e.target.value })}
                  placeholder="SUP-001"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="sup_type">Entity Type</Label>
                <select
                  id="sup_type"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                  value={formData.type}
                  onChange={(e) =>
                    setFormData({ ...formData, type: e.target.value as "BUSINESS" | "INDIVIDUAL" })
                  }
                >
                  <option value="BUSINESS">Registered Business</option>
                  <option value="INDIVIDUAL">Individual Vendor</option>
                </select>
              </div>

              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="gstin">GSTIN Number (15 Characters)</Label>
                <Input
                  id="gstin"
                  value={formData.gstin}
                  onChange={(e) => setFormData({ ...formData, gstin: e.target.value })}
                  placeholder="27AAAAA0000A1Z5"
                  maxLength={15}
                />
                {formErrors.gstin && <p className="text-xs text-destructive">{formErrors.gstin}</p>}
              </div>

              <div className="space-y-1">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+91 98765 43210"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="vendor@company.com"
                />
                {formErrors.email && <p className="text-xs text-destructive">{formErrors.email}</p>}
              </div>

              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="address">Street Address</Label>
                <Textarea
                  id="address"
                  rows={2}
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Building, street name, industrial zone…"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="Mumbai"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="state">State</Label>
                <Input
                  id="state"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  placeholder="Maharashtra"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="pincode">Postal Pincode</Label>
                <Input
                  id="pincode"
                  value={formData.pincode}
                  onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                  placeholder="400001"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="credit_limit">Credit Limit (₹)</Label>
                <Input
                  id="credit_limit"
                  value={formData.credit_limit}
                  onChange={(e) => setFormData({ ...formData, credit_limit: e.target.value })}
                  placeholder="100000"
                />
              </div>
            </div>

            <DialogFooter className="pt-2">
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="shadow-sm"
              >
                {selectedSupplier ? "Save Changes" : "Register Supplier"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* CONFIRM DEACTIVATION DIALOG */}
      <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Deactivate Supplier Profile?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground">
            Are you sure you want to deactivate this supplier profile? Inactive suppliers will be
            hidden from new purchase forms.
          </div>
          <DialogFooter className="pt-2">
            <Button variant="outline" onClick={() => setIsConfirmOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deactivatingId && deleteMutation.mutate(deactivatingId)}
              disabled={deleteMutation.isPending}
            >
              Deactivate Supplier
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* SUPPLIER DETAIL VIEW DRAWER */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent className="sm:max-w-md overflow-y-auto">
          <SheetHeader className="pb-4 border-b">
            <SheetTitle className="text-lg font-bold">{detailSupplier?.name}</SheetTitle>
            <div className="flex gap-2 items-center mt-1">
              <Badge variant="secondary">{detailSupplier?.type || "BUSINESS"}</Badge>
              <Badge
                variant={detailSupplier?.is_active ? "outline" : "destructive"}
                className="text-[10px]"
              >
                {detailSupplier?.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
          </SheetHeader>

          {detailSupplier && (
            <div className="py-6 space-y-6">
              <div className="grid grid-cols-2 gap-4 bg-muted/30 p-4 rounded-xl">
                <div>
                  <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block">
                    Outstanding Payable
                  </span>
                  <span className="text-xl font-bold text-foreground">
                    ₹{(detailSupplier.outstanding_balance || 0).toLocaleString("en-IN")}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block">
                    Credit Limit
                  </span>
                  <span className="text-xl font-bold text-foreground">
                    {detailSupplier.credit_limit
                      ? `₹${detailSupplier.credit_limit.toLocaleString("en-IN")}`
                      : "No Limit"}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Contact Information
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Phone className="h-4 w-4 shrink-0" />
                    <span className="text-foreground font-medium">
                      {detailSupplier.phone || "No phone provided"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Mail className="h-4 w-4 shrink-0" />
                    <span className="text-foreground font-medium">
                      {detailSupplier.email || "No email provided"}
                    </span>
                  </div>
                  <div className="flex items-start gap-2 text-muted-foreground">
                    <MapPin className="h-4 w-4 shrink-0 mt-0.5" />
                    <span className="text-foreground leading-relaxed">
                      {detailSupplier.address || detailSupplier.city || detailSupplier.state
                        ? `${detailSupplier.address ? `${detailSupplier.address}, ` : ""}${detailSupplier.city || ""}${detailSupplier.city && detailSupplier.state ? ", " : ""}${detailSupplier.state || ""} ${detailSupplier.pincode || ""}`
                        : "No address recorded"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Tax & Regulatory Identification
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">GSTIN Number:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailSupplier.gstin || <span className="text-muted-foreground/40">—</span>}
                  </span>

                  <span className="text-muted-foreground">Supplier Code:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailSupplier.supplier_code || (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t text-[10px] text-muted-foreground space-y-1">
                <p>Created Date: {new Date(detailSupplier.created_at).toLocaleString("en-IN")}</p>
                <p>Last Edit Date: {new Date(detailSupplier.updated_at).toLocaleString("en-IN")}</p>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </AppShell>
  );
}

function SuppliersSkeleton() {
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

        <div className="grid gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
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
