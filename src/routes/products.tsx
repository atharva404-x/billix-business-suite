import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
import {
  Plus,
  MoreHorizontal,
  Package,
  Search,
  SlidersHorizontal,
  Download,
  Trash2,
  Edit,
  Eye,
  ArrowUpDown,
  AlertTriangle,
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
import type { Category } from "./categories";

export const Route = createFileRoute("/products")({
  head: () => ({ meta: [{ title: "Products — Billix" }] }),
  component: ProductsPage,
});

export interface Product {
  id: string;
  business_id: string;
  category_id?: string | null;
  unit_id?: string | null;
  sku?: string | null;
  barcode?: string | null;
  name: string;
  description?: string | null;
  hsn_sac_code?: string | null;
  gst_rate?: number | null;
  purchase_price?: number | null;
  selling_price?: number | null;
  opening_stock?: number | null;
  current_stock: number;
  minimum_stock?: number | null;
  maximum_stock?: number | null;
  is_service: boolean;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

interface ProductListResponse {
  items: Product[];
  total: number;
}

interface CategoryListResponse {
  items: Category[];
  total: number;
}

function stockStatus(stock: number, minStock?: number | null) {
  if (stock <= 0) return "Out of Stock";
  if (minStock && stock <= minStock) return "Low Stock";
  if (stock < 10) return "Low Stock";
  return "In Stock";
}

function ProductsPage() {
  const queryClient = useQueryClient();
  const { activeBusinessId } = useBusiness();

  // 1. Filter state variables
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "created_at" | "selling_price" | undefined>(
    undefined,
  );
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // 2. Selection and modal states
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [detailProduct, setDetailProduct] = useState<Product | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | null>(null);

  // 3. Form input states
  const [formData, setFormData] = useState({
    name: "",
    category_id: "",
    sku: "",
    barcode: "",
    hsn_sac_code: "",
    gst_rate: "",
    purchase_price: "",
    selling_price: "",
    opening_stock: "0",
    minimum_stock: "",
    is_service: false,
    description: "",
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

  // 5. Query Products from API
  const { data, isLoading, error, refetch } = useBusinessQuery<ProductListResponse>(
    ["products", page, limit, debouncedSearch, sortBy, sortOrder],
    `/api/v1/products?skip=${(page - 1) * limit}&limit=${limit}${
      debouncedSearch ? `&search_query=${encodeURIComponent(debouncedSearch)}` : ""
    }${sortBy ? `&sort_by=${sortBy}&sort_order=${sortOrder}` : ""}`,
  );

  // 6. Query Categories dynamically for dropdown selection
  const { data: categoriesData } = useBusinessQuery<CategoryListResponse>(
    ["categories", "dropdown"],
    "/api/v1/categories?limit=100",
  );
  const categoryMap = new Map((categoriesData?.items || []).map((c) => [c.id, c.name]));

  // 7. Mutations
  const createMutation = useMutation({
    mutationFn: (payload: Partial<Product>) => {
      return apiClient<Product>("/api/v1/products", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("product:create", queryClient);
      toast.success("Product profile registered successfully.");
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create product.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (vars: { id: string; payload: Partial<Product> }) => {
      return apiClient<Product>(`/api/v1/products/${vars.id}`, {
        method: "PATCH",
        body: JSON.stringify(vars.payload),
      });
    },
    onSuccess: () => {
      invalidateCache("product:update", queryClient);
      toast.success("Product details updated successfully.");
      setIsDialogOpen(false);
      resetForm();
      if (detailProduct && detailProduct.id === selectedProduct?.id) {
        setIsSheetOpen(false);
        setDetailProduct(null);
      }
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update product.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => {
      return apiClient<Product>(`/api/v1/products/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      invalidateCache("product:delete", queryClient);
      toast.success("Product deactivated successfully.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to deactivate product.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      category_id: "",
      sku: "",
      barcode: "",
      hsn_sac_code: "",
      gst_rate: "",
      purchase_price: "",
      selling_price: "",
      opening_stock: "0",
      minimum_stock: "",
      is_service: false,
      description: "",
    });
    setFormErrors({});
    setSelectedProduct(null);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.name.trim()) {
      errors.name = "Product name is required.";
    }
    if (formData.gst_rate) {
      const parsedGst = parseFloat(formData.gst_rate);
      if (isNaN(parsedGst) || parsedGst < 0 || parsedGst > 100) {
        errors.gst_rate = "GST rate must be between 0 and 100%.";
      }
    }
    if (formData.selling_price) {
      const parsedPrice = parseFloat(formData.selling_price);
      if (isNaN(parsedPrice) || parsedPrice < 0) {
        errors.selling_price = "Selling price must be a valid positive number.";
      }
    }
    if (formData.purchase_price) {
      const parsedPrice = parseFloat(formData.purchase_price);
      if (isNaN(parsedPrice) || parsedPrice < 0) {
        errors.purchase_price = "Purchase price must be a valid positive number.";
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
      category_id: formData.category_id || null,
      sku: formData.sku.trim() || null,
      barcode: formData.barcode.trim() || null,
      hsn_sac_code: formData.hsn_sac_code.trim() || null,
      gst_rate: formData.gst_rate ? parseFloat(formData.gst_rate) : null,
      purchase_price: formData.purchase_price ? parseFloat(formData.purchase_price) : null,
      selling_price: formData.selling_price ? parseFloat(formData.selling_price) : null,
      opening_stock: formData.opening_stock ? parseFloat(formData.opening_stock) : 0,
      minimum_stock: formData.minimum_stock ? parseFloat(formData.minimum_stock) : null,
      is_service: formData.is_service,
      description: formData.description.trim() || null,
    };

    if (selectedProduct) {
      updateMutation.mutate({ id: selectedProduct.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleEditClick = (p: Product) => {
    setSelectedProduct(p);
    setFormData({
      name: p.name || "",
      category_id: p.category_id || "",
      sku: p.sku || "",
      barcode: p.barcode || "",
      hsn_sac_code: p.hsn_sac_code || "",
      gst_rate: p.gst_rate !== undefined && p.gst_rate !== null ? String(p.gst_rate) : "",
      purchase_price:
        p.purchase_price !== undefined && p.purchase_price !== null ? String(p.purchase_price) : "",
      selling_price:
        p.selling_price !== undefined && p.selling_price !== null ? String(p.selling_price) : "",
      opening_stock: String(p.opening_stock || 0),
      minimum_stock:
        p.minimum_stock !== undefined && p.minimum_stock !== null ? String(p.minimum_stock) : "",
      is_service: p.is_service || false,
      description: p.description || "",
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

  const handleSort = (field: "name" | "created_at" | "selling_price") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const viewDetails = (p: Product) => {
    setDetailProduct(p);
    setIsSheetOpen(true);
  };

  // Render visual skeletons during loader transitions
  if (isLoading) {
    return <ProductsSkeleton />;
  }

  // Handle server connection error states
  if (error) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load products"
            description={error.message || "Could not retrieve catalog item records."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;

  // KPI computations derived directly from active backend response
  const lowStockCount = items.filter(
    (p) => stockStatus(p.current_stock, p.minimum_stock) === "Low Stock",
  ).length;
  const totalInventoryValue = items.reduce(
    (sum, p) => sum + p.current_stock * (p.purchase_price || p.selling_price || 0),
    0,
  );

  return (
    <AppShell>
      <PageHeader
        title="Products"
        description="Your item catalogue with pricing, GST and stock."
        actions={
          <Button onClick={handleCreateClick} className="gap-1.5 shadow-sm">
            <Plus className="h-4 w-4" /> Add Product
          </Button>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard label="Total SKUs" value={total.toLocaleString("en-IN")} icon={Package} />
        <KpiCard
          label="Active Categories"
          value={(categoriesData?.total || 0).toLocaleString("en-IN")}
        />
        <KpiCard
          label="Low Stock Alerts"
          value={lowStockCount.toLocaleString("en-IN")}
          trend={lowStockCount > 0 ? "down" : "up"}
          change={lowStockCount > 0 ? "attention" : ""}
        />
        <KpiCard
          label="Inventory Value"
          value={`₹${totalInventoryValue.toLocaleString("en-IN")}`}
          trend="up"
          change=""
        />
      </div>

      <Card className="shadow-sm border">
        <CardContent className="p-4 md:p-6">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 sm:flex sm:justify-between mb-4">
            <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search products by name, SKU or HSN…"
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
              title={search ? "No matching products found" : "No products added yet"}
              description={
                search
                  ? "Try refining your search keyword or SKU."
                  : "Register your first product entry to populate invoice billings and stock levels."
              }
              actionText={search ? undefined : "Create First Product"}
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
                              setSelectedIds(new Set(items.map((p) => p.id)));
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
                          Product <ArrowUpDown className="h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>SKU / Barcode</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead className="text-right">Selling Price</TableHead>
                      <TableHead>GST Rate</TableHead>
                      <TableHead className="text-right">Current Stock</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-10" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((p) => {
                      const categoryName = p.category_id
                        ? categoryMap.get(p.category_id)
                        : "Uncategorized";
                      const statusText = stockStatus(p.current_stock, p.minimum_stock);

                      return (
                        <TableRow key={p.id}>
                          <TableCell>
                            <Checkbox
                              checked={selectedIds.has(p.id)}
                              onCheckedChange={(checked) => {
                                const next = new Set(selectedIds);
                                if (checked) next.add(p.id);
                                else next.delete(p.id);
                                setSelectedIds(next);
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <button
                              onClick={() => viewDetails(p)}
                              className="text-left font-semibold text-primary hover:underline block"
                            >
                              {p.name}
                            </button>
                            <span className="text-[10px] text-muted-foreground">
                              {p.is_service ? "Service Item" : "Physical Goods"}
                            </span>
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {p.sku || p.barcode || (
                              <span className="text-muted-foreground/40">—</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="font-medium">
                              {categoryName || "General"}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-semibold">
                            ₹{(p.selling_price || 0).toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell>{p.gst_rate ? `${p.gst_rate}%` : "0%"}</TableCell>
                          <TableCell className="text-right font-medium">
                            {p.is_service ? "N/A" : p.current_stock}
                          </TableCell>
                          <TableCell>
                            <StatusBadge status={statusText} />
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
                                  onClick={() => viewDetails(p)}
                                >
                                  <Eye className="mr-2 h-4 w-4" /> View Details
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  className="cursor-pointer"
                                  onClick={() => handleEditClick(p)}
                                >
                                  <Edit className="mr-2 h-4 w-4" /> Edit Product
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  className="text-destructive focus:text-destructive cursor-pointer"
                                  onClick={() => handleDeactivateClick(p.id)}
                                >
                                  <Trash2 className="mr-2 h-4 w-4" /> Deactivate
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      );
                    })}
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

      {/* CREATE & EDIT PRODUCT DIALOG */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedProduct ? "Edit Product Profile" : "Create New Product Entry"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="prod_name">Product Name *</Label>
                <Input
                  id="prod_name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Enter product title or SKU name"
                />
                {formErrors.name && <p className="text-xs text-destructive">{formErrors.name}</p>}
              </div>

              <div className="space-y-1">
                <Label htmlFor="category_id">Category</Label>
                <select
                  id="category_id"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                >
                  <option value="">-- Select Category --</option>
                  {(categoriesData?.items || []).map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <Label htmlFor="sku">SKU Code</Label>
                <Input
                  id="sku"
                  value={formData.sku}
                  onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                  placeholder="SKU-9920"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="barcode">Barcode</Label>
                <Input
                  id="barcode"
                  value={formData.barcode}
                  onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                  placeholder="EAN / UPC code"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="hsn_sac_code">HSN / SAC Code</Label>
                <Input
                  id="hsn_sac_code"
                  value={formData.hsn_sac_code}
                  onChange={(e) => setFormData({ ...formData, hsn_sac_code: e.target.value })}
                  placeholder="e.g. 3004"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="selling_price">Selling Price (₹)</Label>
                <Input
                  id="selling_price"
                  value={formData.selling_price}
                  onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
                  placeholder="0.00"
                />
                {formErrors.selling_price && (
                  <p className="text-xs text-destructive">{formErrors.selling_price}</p>
                )}
              </div>

              <div className="space-y-1">
                <Label htmlFor="purchase_price">Purchase Price (₹)</Label>
                <Input
                  id="purchase_price"
                  value={formData.purchase_price}
                  onChange={(e) => setFormData({ ...formData, purchase_price: e.target.value })}
                  placeholder="0.00"
                />
                {formErrors.purchase_price && (
                  <p className="text-xs text-destructive">{formErrors.purchase_price}</p>
                )}
              </div>

              <div className="space-y-1">
                <Label htmlFor="gst_rate">GST Tax Rate (%)</Label>
                <Input
                  id="gst_rate"
                  value={formData.gst_rate}
                  onChange={(e) => setFormData({ ...formData, gst_rate: e.target.value })}
                  placeholder="18"
                />
                {formErrors.gst_rate && (
                  <p className="text-xs text-destructive">{formErrors.gst_rate}</p>
                )}
              </div>

              {!selectedProduct && (
                <div className="space-y-1">
                  <Label htmlFor="opening_stock">Opening Stock Qty</Label>
                  <Input
                    id="opening_stock"
                    value={formData.opening_stock}
                    onChange={(e) => setFormData({ ...formData, opening_stock: e.target.value })}
                    placeholder="0"
                  />
                </div>
              )}

              <div className="space-y-1">
                <Label htmlFor="minimum_stock">Minimum Low Stock Alert Qty</Label>
                <Input
                  id="minimum_stock"
                  value={formData.minimum_stock}
                  onChange={(e) => setFormData({ ...formData, minimum_stock: e.target.value })}
                  placeholder="10"
                />
              </div>

              <div className="space-y-1 sm:col-span-2 pt-2">
                <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_service}
                    onChange={(e) => setFormData({ ...formData, is_service: e.target.checked })}
                    className="h-4 w-4 cursor-pointer"
                  />
                  This is a service item (No physical inventory tracking required)
                </label>
              </div>

              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="description">Product Description</Label>
                <Textarea
                  id="description"
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Item specifications or invoicing description details…"
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
                {selectedProduct ? "Save Changes" : "Register Product"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* CONFIRM DEACTIVATION DIALOG */}
      <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Deactivate Product Profile?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground">
            Are you sure you want to deactivate this item entry? Deactivated items will no longer
            appear on new invoice forms.
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
              Deactivate Item
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* PRODUCT DETAIL VIEW DRAWER */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent className="sm:max-w-md overflow-y-auto">
          <SheetHeader className="pb-4 border-b">
            <SheetTitle className="text-lg font-bold">{detailProduct?.name}</SheetTitle>
            <div className="flex gap-2 items-center mt-1">
              <Badge variant="secondary">
                {detailProduct?.category_id
                  ? categoryMap.get(detailProduct.category_id)
                  : "Uncategorized"}
              </Badge>
              <Badge
                variant={detailProduct?.is_active ? "outline" : "destructive"}
                className="text-[10px]"
              >
                {detailProduct?.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
          </SheetHeader>

          {detailProduct && (
            <div className="py-6 space-y-6">
              <div className="grid grid-cols-2 gap-4 bg-muted/30 p-4 rounded-xl">
                <div>
                  <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block">
                    Selling Price
                  </span>
                  <span className="text-xl font-bold text-foreground">
                    ₹{(detailProduct.selling_price || 0).toLocaleString("en-IN")}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider block">
                    Current Stock
                  </span>
                  <span className="text-xl font-bold text-foreground">
                    {detailProduct.is_service ? "Service" : detailProduct.current_stock}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Specifications & Codes
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">SKU Code:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailProduct.sku || <span className="text-muted-foreground/40">—</span>}
                  </span>

                  <span className="text-muted-foreground">Barcode:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailProduct.barcode || <span className="text-muted-foreground/40">—</span>}
                  </span>

                  <span className="text-muted-foreground">HSN / SAC Code:</span>
                  <span className="font-mono text-foreground font-medium text-right">
                    {detailProduct.hsn_sac_code || (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </span>

                  <span className="text-muted-foreground">GST Tax Rate:</span>
                  <span className="text-foreground font-medium text-right">
                    {detailProduct.gst_rate ? `${detailProduct.gst_rate}%` : "0%"}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Cost & Inventory Limits
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">Purchase Price:</span>
                  <span className="text-foreground font-medium text-right">
                    {detailProduct.purchase_price ? (
                      `₹${detailProduct.purchase_price.toLocaleString("en-IN")}`
                    ) : (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </span>

                  <span className="text-muted-foreground">Minimum Low Stock Qty:</span>
                  <span className="text-foreground font-medium text-right">
                    {detailProduct.minimum_stock ?? (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Description
                </h4>
                <div className="text-sm rounded-lg border p-3 bg-card text-muted-foreground leading-relaxed">
                  {detailProduct.description || "No item description provided."}
                </div>
              </div>

              <div className="pt-4 border-t text-[10px] text-muted-foreground space-y-1">
                <p>Created Date: {new Date(detailProduct.created_at).toLocaleString("en-IN")}</p>
                <p>Last Edit Date: {new Date(detailProduct.updated_at).toLocaleString("en-IN")}</p>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </AppShell>
  );
}

function ProductsSkeleton() {
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

        <div className="grid gap-4 sm:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
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
