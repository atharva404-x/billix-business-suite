import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
import {
  Plus,
  MoreHorizontal,
  Users,
  Search,
  SlidersHorizontal,
  Download,
  Trash2,
  Edit,
  Eye,
  ArrowUpDown,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import { useUser } from "@clerk/clerk-react";
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
import { KpiCard } from "@/components/common/kpi-card";
import { SimplePagination } from "@/components/common/simple-pagination";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

export const Route = createFileRoute("/customers")({
  head: () => ({ meta: [{ title: "Customers — Billix" }] }),
  component: CustomersPage,
});

export interface Customer {
  id: string;
  customer_code?: string | null;
  name: string;
  type: "B2B" | "B2C";
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

interface CustomerListResponse {
  items: Customer[];
  total: number;
}

function CustomersPage() {
  const queryClient = useQueryClient();
  const { activeBusinessId } = useBusiness();

  // 1. Grid/List parameters state
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "created_at" | "updated_at" | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // 2. Selection states
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // 3. Modals and drawers state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [detailCustomer, setDetailCustomer] = useState<Customer | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | null>(null);

  // 4. Form state variables
  const [formData, setFormData] = useState({
    name: "",
    type: "B2C" as "B2C" | "B2B",
    gstin: "",
    phone: "",
    email: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    credit_limit: "",
    customer_code: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // 5. Debounce input value changes
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // Reset page to 1 when search filters change
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  // 6. Multi-tenant list fetch query
  const { data, isLoading, error, refetch } = useBusinessQuery<CustomerListResponse>(
    ["customers", page, limit, debouncedSearch, sortBy, sortOrder],
    `${API_ENDPOINTS.customers.list}?skip=${(page - 1) * limit}&limit=${limit}${
      debouncedSearch ? `&search_query=${encodeURIComponent(debouncedSearch)}` : ""
    }${sortBy ? `&sort_by=${sortBy}&sort_order=${sortOrder}` : ""}`,
  );

  // 7. Mutations triggers
  const createMutation = useMutation({
    mutationFn: (
      newCustomer: Omit<
        Customer,
        "id" | "created_at" | "updated_at" | "outstanding_balance" | "is_active"
      >,
    ) => {
      return apiClient<Customer>(API_ENDPOINTS.customers.create, {
        method: "POST",
        body: JSON.stringify(newCustomer),
      });
    },
    onSuccess: () => {
      invalidateCache("customer:create", queryClient);
      toast.success("Customer profile created successfully.");
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create customer.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (vars: { id: string; payload: Partial<Customer> }) => {
      return apiClient<Customer>(`${API_ENDPOINTS.customers.list}/${vars.id}`, {
        method: "PATCH",
        body: JSON.stringify(vars.payload),
      });
    },
    onSuccess: () => {
      invalidateCache("customer:update", queryClient);
      toast.success("Customer profile updated successfully.");
      setIsDialogOpen(false);
      resetForm();
      if (detailCustomer && detailCustomer.id === selectedCustomer?.id) {
        // Refresh details drawer if the active row was updated
        setDetailCustomer(null);
        setIsSheetOpen(false);
      }
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update customer.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => {
      return apiClient<Customer>(`${API_ENDPOINTS.customers.list}/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      invalidateCache("customer:delete", queryClient);
      toast.success("Customer profile deactivated successfully.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to deactivate customer.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      type: "B2C",
      gstin: "",
      phone: "",
      email: "",
      address: "",
      city: "",
      state: "",
      pincode: "",
      credit_limit: "",
      customer_code: "",
    });
    setFormErrors({});
    setSelectedCustomer(null);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.name.trim()) {
      errors.name = "Customer name is required.";
    }
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = "Invalid email format.";
    }
    if (formData.gstin) {
      if (formData.gstin.length !== 15) {
        errors.gstin = "GSTIN must be exactly 15 characters.";
      }
    }
    if (formData.type === "B2B" && !formData.gstin) {
      errors.gstin = "GSTIN is required for B2B customers.";
    }
    if (formData.credit_limit) {
      const parsed = parseFloat(formData.credit_limit);
      if (isNaN(parsed) || parsed < 0) {
        errors.credit_limit = "Credit limit must be a positive number.";
      }
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
      name: formData.name.trim(),
      type: formData.type,
      phone: formData.phone.trim() || null,
      email: formData.email.trim() || null,
      address: formData.address.trim() || null,
      city: formData.city.trim() || null,
      state: formData.state.trim() || null,
      pincode: formData.pincode.trim() || null,
      credit_limit: formData.credit_limit ? parseFloat(formData.credit_limit) : null,
      customer_code: formData.customer_code.trim() || null,
      gstin: formData.gstin.trim() ? formData.gstin.trim().toUpperCase() : null,
    };

    if (selectedCustomer) {
      updateMutation.mutate({ id: selectedCustomer.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleEditClick = (c: Customer) => {
    setSelectedCustomer(c);
    setFormData({
      name: c.name || "",
      type: c.type || "B2C",
      gstin: c.gstin || "",
      phone: c.phone || "",
      email: c.email || "",
      address: c.address || "",
      city: c.city || "",
      state: c.state || "",
      pincode: c.pincode || "",
      credit_limit:
        c.credit_limit !== undefined && c.credit_limit !== null ? String(c.credit_limit) : "",
      customer_code: c.customer_code || "",
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

  const handleSort = (field: "name" | "created_at" | "updated_at") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const handleRowSelect = (id: string, checked: boolean) => {
    const next = new Set(selectedIds);
    if (checked) {
      next.add(id);
    } else {
      next.delete(id);
    }
    setSelectedIds(next);
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked && data?.items) {
      setSelectedIds(new Set(data.items.map((c) => c.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const viewDetails = (c: Customer) => {
    setDetailCustomer(c);
    setIsSheetOpen(true);
  };

  // Render visual skeletons during loader fetch transitions
  if (isLoading) {
    return <CustomersSkeleton />;
  }

  // Handle server connection error states
  if (error) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load customers"
            description={error.message || "Could not retrieve customer database entries."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;

  // Compute stat card numbers derived directly from the database response
  const activeCount = items.filter((c) => c.is_active).length;
  const totalOutstanding = items.reduce((sum, c) => sum + (c.outstanding_balance || 0), 0);

  return (
    <AppShell>
      <PageHeader
        title="Customers"
        description="Manage buyers, GSTINs, credit limits and outstanding balances."
        actions={
          <Button onClick={handleCreateClick} className="gap-1.5 shadow-sm">
            <Plus className="h-4 w-4" /> Add Customer
          </Button>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <KpiCard
          label="Total Customers"
          value={total.toLocaleString("en-IN")}
          hint="registered profiles"
          icon={Users}
        />
        <KpiCard
          label="Active Accounts"
          value={activeCount.toLocaleString("en-IN")}
          trend="up"
          change=""
          hint="active in database"
        />
        <KpiCard
          label="Total Outstanding"
          value={`₹${totalOutstanding.toLocaleString("en-IN")}`}
          trend={totalOutstanding > 0 ? "up" : "down"}
          change=""
          hint="outstanding receivables sum"
        />
      </div>

      <Card className="shadow-sm border">
        <CardContent className="p-4 md:p-6">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 sm:flex sm:justify-between mb-4">
            <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search customers by name, phone or GSTIN…"
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
              title={search ? "No matches found" : "No customers registered"}
              description={
                search
                  ? "Try refining your search terms or search by phone/GSTIN numbers."
                  : "Create your first customer profile to start raising invoices."
              }
              actionText={search ? undefined : "Add Customer"}
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
                          onCheckedChange={(checked) => handleSelectAll(!!checked)}
                        />
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          onClick={() => handleSort("name")}
                          className="h-8 gap-1 p-0 hover:bg-transparent font-semibold text-xs"
                        >
                          Customer <ArrowUpDown className="h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>GSTIN</TableHead>
                      <TableHead>Phone</TableHead>
                      <TableHead>City</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead className="text-right">Balance</TableHead>
                      <TableHead className="w-10" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((c) => (
                      <TableRow key={c.id}>
                        <TableCell>
                          <Checkbox
                            checked={selectedIds.has(c.id)}
                            onCheckedChange={(checked) => handleRowSelect(c.id, !!checked)}
                          />
                        </TableCell>
                        <TableCell>
                          <button
                            onClick={() => viewDetails(c)}
                            className="text-left font-semibold text-primary hover:underline block"
                          >
                            {c.name}
                          </button>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            {c.customer_code || c.id.slice(0, 8)}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {c.gstin || <span className="text-muted-foreground/50">—</span>}
                        </TableCell>
                        <TableCell>
                          {c.phone || <span className="text-muted-foreground/50">—</span>}
                        </TableCell>
                        <TableCell>
                          {c.city || <span className="text-muted-foreground/50">—</span>}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="font-medium">
                            {c.type}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          ₹{(c.outstanding_balance || 0).toLocaleString("en-IN")}
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
                                onClick={() => viewDetails(c)}
                              >
                                <Eye className="mr-2 h-4 w-4" /> View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={() => handleEditClick(c)}
                              >
                                <Edit className="mr-2 h-4 w-4" /> Edit Profile
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="text-destructive focus:text-destructive cursor-pointer"
                                onClick={() => handleDeactivateClick(c.id)}
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

      {/* CREATE & EDIT CUSTOMER DIALOG */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {selectedCustomer ? "Edit Customer Details" : "Register New Customer"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <Label htmlFor="name">Customer Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Enter buyer name"
                />
                {formErrors.name && <p className="text-xs text-destructive">{formErrors.name}</p>}
              </div>

              <div className="space-y-1">
                <Label htmlFor="type">Customer Type</Label>
                <div className="flex h-9 items-center gap-4">
                  <label className="flex items-center gap-1.5 text-sm font-medium cursor-pointer">
                    <input
                      type="radio"
                      name="type"
                      checked={formData.type === "B2C"}
                      onChange={() => setFormData({ ...formData, type: "B2C" })}
                      className="cursor-pointer"
                    />
                    B2C (Individual)
                  </label>
                  <label className="flex items-center gap-1.5 text-sm font-medium cursor-pointer">
                    <input
                      type="radio"
                      name="type"
                      checked={formData.type === "B2B"}
                      onChange={() => setFormData({ ...formData, type: "B2B" })}
                      className="cursor-pointer"
                    />
                    B2B (Business)
                  </label>
                </div>
              </div>

              <div className="space-y-1">
                <Label htmlFor="gstin">GSTIN {formData.type === "B2B" && "*"}</Label>
                <Input
                  id="gstin"
                  value={formData.gstin}
                  onChange={(e) =>
                    setFormData({ ...formData, gstin: e.target.value.toUpperCase() })
                  }
                  maxLength={15}
                  placeholder="15-digit GST number"
                />
                {formErrors.gstin && <p className="text-xs text-destructive">{formErrors.gstin}</p>}
              </div>

              <div className="space-y-1">
                <Label htmlFor="customer_code">Customer Code</Label>
                <Input
                  id="customer_code"
                  value={formData.customer_code}
                  onChange={(e) => setFormData({ ...formData, customer_code: e.target.value })}
                  placeholder="CUST-1002"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="Enter phone number"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Enter email address"
                />
                {formErrors.email && <p className="text-xs text-destructive">{formErrors.email}</p>}
              </div>

              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Street address details"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="Enter city"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="state">State</Label>
                <Input
                  id="state"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  placeholder="Enter state"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="pincode">Postal Code (Pincode)</Label>
                <Input
                  id="pincode"
                  value={formData.pincode}
                  onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                  placeholder="6-digit ZIP code"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="credit_limit">Credit Limit (₹)</Label>
                <Input
                  id="credit_limit"
                  value={formData.credit_limit}
                  onChange={(e) => setFormData({ ...formData, credit_limit: e.target.value })}
                  placeholder="Enter credit ceiling limit"
                />
                {formErrors.credit_limit && (
                  <p className="text-xs text-destructive">{formErrors.credit_limit}</p>
                )}
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
                {selectedCustomer ? "Save Changes" : "Register Profile"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* CONFIRM DEACTIVATION DIALOG */}
      <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Deactivate Customer Profile?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground">
            Are you sure you want to deactivate this customer account? Active invoicing features for
            this customer will be disabled. This profile can be reactivated later.
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
              Deactivate Account
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* CUSTOMER DETAIL VIEW DRAWER */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent className="sm:max-w-md overflow-y-auto">
          <SheetHeader className="pb-4 border-b">
            <SheetTitle className="text-lg font-bold">{detailCustomer?.name}</SheetTitle>
            <div className="flex gap-2 items-center mt-1">
              <Badge variant={detailCustomer?.type === "B2B" ? "default" : "secondary"}>
                {detailCustomer?.type}
              </Badge>
              <Badge
                variant={detailCustomer?.is_active ? "outline" : "destructive"}
                className="text-[10px]"
              >
                {detailCustomer?.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
          </SheetHeader>

          {detailCustomer && (
            <div className="py-6 space-y-6">
              <div className="bg-muted/30 p-4 rounded-xl space-y-1">
                <span className="text-xs text-muted-foreground font-semibold uppercase tracking-wider block">
                  Outstanding Balance
                </span>
                <span className="text-2xl font-bold text-foreground">
                  ₹{(detailCustomer.outstanding_balance || 0).toLocaleString("en-IN")}
                </span>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Registration Details
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">Customer Code:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailCustomer.customer_code || (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </span>

                  <span className="text-muted-foreground">GSTIN Number:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailCustomer.gstin || <span className="text-muted-foreground/40">—</span>}
                  </span>

                  <span className="text-muted-foreground">Credit Limit:</span>
                  <span className="text-foreground font-medium text-right">
                    {detailCustomer.credit_limit ? (
                      `₹${detailCustomer.credit_limit.toLocaleString("en-IN")}`
                    ) : (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Contact Information
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">Phone Number:</span>
                  <span className="text-foreground font-medium text-right">
                    {detailCustomer.phone || <span className="text-muted-foreground/40">—</span>}
                  </span>

                  <span className="text-muted-foreground">Email Address:</span>
                  <span className="text-foreground font-medium text-right truncate">
                    {detailCustomer.email || <span className="text-muted-foreground/40">—</span>}
                  </span>

                  <span className="text-muted-foreground">Postal Code:</span>
                  <span className="text-foreground font-medium text-right">
                    {detailCustomer.pincode || <span className="text-muted-foreground/40">—</span>}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Billing Location
                </h4>
                <div className="text-sm rounded-lg border p-3 space-y-1 bg-card">
                  <p className="text-foreground font-medium">
                    {detailCustomer.address || "No address listed"}
                  </p>
                  <p className="text-muted-foreground text-xs">
                    {[detailCustomer.city, detailCustomer.state].filter(Boolean).join(", ")}
                  </p>
                </div>
              </div>

              <div className="pt-4 border-t text-[10px] text-muted-foreground space-y-1">
                <p>
                  Profile registered: {new Date(detailCustomer.created_at).toLocaleString("en-IN")}
                </p>
                <p>
                  Last profile edit: {new Date(detailCustomer.updated_at).toLocaleString("en-IN")}
                </p>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </AppShell>
  );
}

function CustomersSkeleton() {
  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 animate-pulse rounded bg-muted/60" />
            <div className="h-4 w-80 animate-pulse rounded bg-muted/60" />
          </div>
          <div className="h-9 w-32 animate-pulse rounded bg-muted/60" />
        </div>

        {/* KPI Cards Skeleton */}
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

        {/* Table Skeleton */}
        <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-2">
            <div className="h-9 w-64 animate-pulse rounded bg-muted/60" />
            <div className="flex gap-2">
              <div className="h-9 w-20 animate-pulse rounded bg-muted/60" />
              <div className="h-9 w-20 animate-pulse rounded bg-muted/60" />
            </div>
          </div>
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
