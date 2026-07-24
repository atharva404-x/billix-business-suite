import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
import {
  Plus,
  ArrowUpDown,
  Boxes,
  AlertTriangle,
  History as HistoryIcon,
  Search,
  SlidersHorizontal,
  Package,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { KpiCard } from "@/components/common/kpi-card";
import { StatusBadge } from "@/components/common/status-badge";
import { SimplePagination } from "@/components/common/simple-pagination";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

import type { Product } from "./products";
import type { Category } from "./categories";

export const Route = createFileRoute("/inventory")({
  head: () => ({ meta: [{ title: "Inventory — Billix" }] }),
  component: InventoryPage,
});

interface ProductListResponse {
  items: Product[];
  total: number;
}

interface CategoryListResponse {
  items: Category[];
  total: number;
}

interface InventoryTransaction {
  id: string;
  business_id: string;
  product_id: string;
  transaction_type: string;
  quantity: number;
  previous_stock: number;
  new_stock: number;
  reference_type?: string | null;
  reference_id?: string | null;
  remarks?: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface InventoryHistoryListResponse {
  items: InventoryTransaction[];
  total: number;
}

function stockStatus(stock: number, minStock?: number | null) {
  if (stock <= 0) return "Out of Stock";
  if (minStock && stock <= minStock) return "Low Stock";
  if (stock < 10) return "Low Stock";
  return "In Stock";
}

function InventoryPage() {
  const queryClient = useQueryClient();
  const { activeBusinessId } = useBusiness();

  // 1. Filter and sorting state
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "created_at" | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // 2. Modals state
  const [isAdjustOpen, setIsAdjustOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [historyProduct, setHistoryProduct] = useState<Product | null>(null);

  // 3. Form input states
  const [adjustForm, setAdjustForm] = useState({
    product_id: "",
    adjustment_type: "stock-in" as "stock-in" | "stock-out" | "adjustment",
    quantity: "",
    remarks: "",
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

  // 5. Query product stock list from backend API
  const { data, isLoading, error, refetch } = useBusinessQuery<ProductListResponse>(
    ["products", "inventory", page, limit, debouncedSearch, sortBy, sortOrder],
    `/api/v1/products?skip=${(page - 1) * limit}&limit=${limit}${
      debouncedSearch ? `&search_query=${encodeURIComponent(debouncedSearch)}` : ""
    }${sortBy ? `&sort_by=${sortBy}&sort_order=${sortOrder}` : ""}`,
  );

  // 6. Query categories list for category badges
  const { data: categoriesData } = useBusinessQuery<CategoryListResponse>(
    ["categories", "dropdown"],
    "/api/v1/categories?limit=100",
  );
  const categoryMap = new Map((categoriesData?.items || []).map((c) => [c.id, c.name]));

  // 7. Query movement transaction history when item sheet opens
  const {
    data: historyData,
    isLoading: isHistoryLoading,
    refetch: refetchHistory,
  } = useBusinessQuery<InventoryHistoryListResponse>(
    ["inventory", "history", historyProduct?.id || ""],
    `/api/v1/inventory/history/${historyProduct?.id || ""}?limit=50`,
    { enabled: !!historyProduct?.id && isHistoryOpen },
  );

  // 8. Adjustment mutations
  const stockInMutation = useMutation({
    mutationFn: (payload: { product_id: string; quantity: number; remarks?: string }) => {
      return apiClient<InventoryTransaction>("/api/v1/inventory/stock-in", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("inventory:adjust", queryClient);
      toast.success("Stock intake recorded successfully.");
      setIsAdjustOpen(false);
      resetAdjustForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to process stock intake.");
    },
  });

  const stockOutMutation = useMutation({
    mutationFn: (payload: { product_id: string; quantity: number; remarks?: string }) => {
      return apiClient<InventoryTransaction>("/api/v1/inventory/stock-out", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("inventory:adjust", queryClient);
      toast.success("Stock deduction recorded successfully.");
      setIsAdjustOpen(false);
      resetAdjustForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to process stock deduction.");
    },
  });

  const adjustmentMutation = useMutation({
    mutationFn: (payload: { product_id: string; quantity: number; remarks?: string }) => {
      return apiClient<InventoryTransaction>("/api/v1/inventory/adjustment", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("inventory:adjust", queryClient);
      toast.success("Stock adjustment delta saved successfully.");
      setIsAdjustOpen(false);
      resetAdjustForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to save stock adjustment.");
    },
  });

  const resetAdjustForm = () => {
    setAdjustForm({
      product_id: "",
      adjustment_type: "stock-in",
      quantity: "",
      remarks: "",
    });
    setFormErrors({});
  };

  const validateAdjustForm = () => {
    const errors: Record<string, string> = {};
    if (!adjustForm.product_id) {
      errors.product_id = "Please select a product item.";
    }
    const qtyNum = parseFloat(adjustForm.quantity);
    if (!adjustForm.quantity || isNaN(qtyNum)) {
      errors.quantity = "Please enter a valid quantity.";
    } else if (adjustForm.adjustment_type !== "adjustment" && qtyNum <= 0) {
      errors.quantity = "Quantity must be greater than zero.";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleAdjustSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateAdjustForm()) return;

    const qtyNum = parseFloat(adjustForm.quantity);
    const payload = {
      product_id: adjustForm.product_id,
      quantity: qtyNum,
      remarks: adjustForm.remarks.trim() || undefined,
    };

    if (adjustForm.adjustment_type === "stock-in") {
      stockInMutation.mutate(payload);
    } else if (adjustForm.adjustment_type === "stock-out") {
      stockOutMutation.mutate(payload);
    } else {
      adjustmentMutation.mutate(payload);
    }
  };

  const openAdjustForProduct = (p?: Product) => {
    resetAdjustForm();
    if (p) {
      setAdjustForm((prev) => ({ ...prev, product_id: p.id }));
    }
    setIsAdjustOpen(true);
  };

  const openHistoryForProduct = (p: Product) => {
    setHistoryProduct(p);
    setIsHistoryOpen(true);
  };

  const handleSort = (field: "name" | "created_at") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  // Render visual skeletons during loader transitions
  if (isLoading) {
    return <InventorySkeleton />;
  }

  // Handle server connection error states
  if (error) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load inventory"
            description={error.message || "Could not retrieve catalog inventory records."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;

  // KPI computations derived directly from backend product stock levels
  const lowStockCount = items.filter(
    (p) => stockStatus(p.current_stock, p.minimum_stock) === "Low Stock",
  ).length;
  const outOfStockCount = items.filter((p) => p.current_stock <= 0 && !p.is_service).length;
  const totalUnitsOnHand = items.reduce((sum, p) => sum + (p.is_service ? 0 : p.current_stock), 0);
  const totalValuation = items.reduce(
    (sum, p) =>
      sum + (p.is_service ? 0 : p.current_stock * (p.purchase_price || p.selling_price || 0)),
    0,
  );

  return (
    <AppShell>
      <PageHeader
        title="Inventory & Stock"
        description="Live stock levels, stock movement history and low-stock alerts."
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={() => openAdjustForProduct()}
            >
              <ArrowUpDown className="h-4 w-4" /> Stock Movement
            </Button>
            <Button size="sm" className="gap-1.5 shadow-sm" onClick={() => openAdjustForProduct()}>
              <Plus className="h-4 w-4" /> Adjust Stock
            </Button>
          </>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <KpiCard label="Items in Catalogue" value={total.toLocaleString("en-IN")} icon={Boxes} />
        <KpiCard
          label="Total Units On Hand"
          value={totalUnitsOnHand.toLocaleString("en-IN")}
          icon={Package}
        />
        <KpiCard
          label="Low / Out of Stock"
          value={(lowStockCount + outOfStockCount).toLocaleString("en-IN")}
          icon={AlertTriangle}
          trend={lowStockCount + outOfStockCount > 0 ? "down" : "up"}
          change={lowStockCount + outOfStockCount > 0 ? "attention" : ""}
        />
        <KpiCard
          label="Total Inventory Value"
          value={`₹${totalValuation.toLocaleString("en-IN")}`}
          icon={TrendingUp}
        />
      </div>

      <Card className="shadow-sm border">
        <CardContent className="p-4 md:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
            <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search stock by product name, SKU or barcode…"
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
            </div>
          </div>

          {items.length === 0 ? (
            <EmptyState
              title={search ? "No matching stock items found" : "No inventory recorded yet"}
              description={
                search
                  ? "Try refining your search keyword or barcode."
                  : "Register products in your catalog to start tracking live stock intake and movements."
              }
              actionText={search ? undefined : "Create Product Entry"}
              onActionClick={search ? undefined : () => (window.location.href = "/products")}
            />
          ) : (
            <>
              <div className="overflow-x-auto rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>
                        <Button
                          variant="ghost"
                          onClick={() => handleSort("name")}
                          className="h-8 gap-1 p-0 hover:bg-transparent font-semibold text-xs"
                        >
                          Product Item <ArrowUpDown className="h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>SKU / Barcode</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead className="text-right">Available Stock</TableHead>
                      <TableHead className="text-right">Min Reorder Level</TableHead>
                      <TableHead className="text-right">Est. Valuation</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((p) => {
                      const categoryName = p.category_id
                        ? categoryMap.get(p.category_id)
                        : "Uncategorized";
                      const statusText = stockStatus(p.current_stock, p.minimum_stock);
                      const itemValuation =
                        (p.purchase_price || p.selling_price || 0) * p.current_stock;

                      return (
                        <TableRow key={p.id}>
                          <TableCell>
                            <button
                              onClick={() => openHistoryForProduct(p)}
                              className="font-semibold text-primary hover:underline text-left block"
                            >
                              {p.name}
                            </button>
                            <span className="text-[10px] text-muted-foreground">
                              {p.is_service
                                ? "Service (No Physical Stock)"
                                : `Updated ${new Date(p.updated_at).toLocaleDateString("en-IN")}`}
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
                          <TableCell className="text-right font-bold text-base">
                            {p.is_service ? "N/A" : p.current_stock}
                          </TableCell>
                          <TableCell className="text-right text-muted-foreground text-xs">
                            {p.minimum_stock !== null && p.minimum_stock !== undefined
                              ? p.minimum_stock
                              : 10}
                          </TableCell>
                          <TableCell className="text-right font-semibold text-xs">
                            {p.is_service ? "N/A" : `₹${itemValuation.toLocaleString("en-IN")}`}
                          </TableCell>
                          <TableCell>
                            <StatusBadge status={p.is_service ? "In Stock" : statusText} />
                          </TableCell>
                          <TableCell className="text-right space-x-1">
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-8 gap-1"
                              onClick={() => openAdjustForProduct(p)}
                            >
                              <Plus className="h-3.5 w-3.5" /> Adjust
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-8 gap-1 text-muted-foreground hover:text-foreground"
                              onClick={() => openHistoryForProduct(p)}
                            >
                              <HistoryIcon className="h-3.5 w-3.5" /> History
                            </Button>
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

      {/* STOCK ADJUSTMENT DIALOG MODAL */}
      <Dialog open={isAdjustOpen} onOpenChange={setIsAdjustOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Stock Movement & Adjustment</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAdjustSubmit} className="space-y-4 pt-2">
            <div className="space-y-1">
              <Label htmlFor="adj_prod">Select Product *</Label>
              <select
                id="adj_prod"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                value={adjustForm.product_id}
                onChange={(e) => setAdjustForm({ ...adjustForm, product_id: e.target.value })}
              >
                <option value="">-- Choose Product Entry --</option>
                {items.map((prod) => (
                  <option key={prod.id} value={prod.id}>
                    {prod.name} (Current Stock: {prod.current_stock})
                  </option>
                ))}
              </select>
              {formErrors.product_id && (
                <p className="text-xs text-destructive">{formErrors.product_id}</p>
              )}
            </div>

            <div className="space-y-1">
              <Label htmlFor="adj_type">Action Type</Label>
              <select
                id="adj_type"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
                value={adjustForm.adjustment_type}
                onChange={(e) =>
                  setAdjustForm({
                    ...adjustForm,
                    adjustment_type: e.target.value as "stock-in" | "stock-out" | "adjustment",
                  })
                }
              >
                <option value="stock-in">Stock Intake (+ Add Units)</option>
                <option value="stock-out">Stock Deduction (- Deduct Units)</option>
                <option value="adjustment">Manual Adjustment Delta (+ / - Qty)</option>
              </select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="adj_qty">Quantity *</Label>
              <Input
                id="adj_qty"
                type="number"
                step="any"
                value={adjustForm.quantity}
                onChange={(e) => setAdjustForm({ ...adjustForm, quantity: e.target.value })}
                placeholder="e.g. 25"
              />
              {formErrors.quantity && (
                <p className="text-xs text-destructive">{formErrors.quantity}</p>
              )}
            </div>

            <div className="space-y-1">
              <Label htmlFor="adj_remarks">Remarks / Reason</Label>
              <Textarea
                id="adj_remarks"
                rows={2}
                value={adjustForm.remarks}
                onChange={(e) => setAdjustForm({ ...adjustForm, remarks: e.target.value })}
                placeholder="e.g. Purchase invoice intake, Damaged goods removal, Physical count audit"
              />
            </div>

            <DialogFooter className="pt-2">
              <Button type="button" variant="outline" onClick={() => setIsAdjustOpen(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  stockInMutation.isPending ||
                  stockOutMutation.isPending ||
                  adjustmentMutation.isPending
                }
                className="shadow-sm"
              >
                Save Adjustment
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* MOVEMENT TRANSACTION HISTORY SIDE DRAWER */}
      <Sheet open={isHistoryOpen} onOpenChange={setIsHistoryOpen}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          <SheetHeader className="pb-4 border-b">
            <SheetTitle className="text-lg font-bold">
              Stock Movement Log: {historyProduct?.name}
            </SheetTitle>
            <div className="text-xs text-muted-foreground">
              Current Available Stock:{" "}
              <span className="font-bold text-foreground">
                {historyProduct?.current_stock} units
              </span>
            </div>
          </SheetHeader>

          <div className="py-4 space-y-4">
            {isHistoryLoading ? (
              <div className="space-y-3 pt-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="h-16 w-full animate-pulse rounded-lg border bg-muted/40"
                  />
                ))}
              </div>
            ) : !historyData?.items || historyData.items.length === 0 ? (
              <div className="py-12 text-center text-sm text-muted-foreground">
                No stock movement transactions logged for this item yet.
              </div>
            ) : (
              <div className="space-y-3">
                {historyData.items.map((tx) => {
                  const isPositive = tx.quantity > 0 || tx.transaction_type.includes("IN");
                  return (
                    <div key={tx.id} className="p-3 border rounded-lg bg-card shadow-2xs space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          {isPositive ? (
                            <ArrowUpRight className="h-4 w-4 text-emerald-600" />
                          ) : (
                            <ArrowDownRight className="h-4 w-4 text-rose-600" />
                          )}
                          <Badge
                            variant={isPositive ? "outline" : "destructive"}
                            className="text-[10px]"
                          >
                            {tx.transaction_type}
                          </Badge>
                        </div>
                        <span className="font-mono text-sm font-bold">
                          {isPositive ? `+${tx.quantity}` : `${tx.quantity}`} units
                        </span>
                      </div>

                      <div className="flex justify-between text-xs text-muted-foreground pt-1">
                        <span>Stock Transition:</span>
                        <span className="font-medium text-foreground">
                          {tx.previous_stock} → {tx.new_stock} units
                        </span>
                      </div>

                      {tx.remarks && (
                        <div className="text-xs italic text-muted-foreground bg-muted/30 p-1.5 rounded mt-1">
                          "{tx.remarks}"
                        </div>
                      )}

                      <div className="text-[10px] text-muted-foreground text-right pt-1">
                        {new Date(tx.created_at).toLocaleString("en-IN")}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </SheetContent>
      </Sheet>
    </AppShell>
  );
}

function InventorySkeleton() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 animate-pulse rounded bg-muted/60" />
            <div className="h-4 w-80 animate-pulse rounded bg-muted/60" />
          </div>
          <div className="flex gap-2">
            <div className="h-9 w-32 animate-pulse rounded bg-muted/60" />
            <div className="h-9 w-32 animate-pulse rounded bg-muted/60" />
          </div>
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
