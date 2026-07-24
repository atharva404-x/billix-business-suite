import { createFileRoute } from "@tanstack/react-router";
import React, { useState, useEffect } from "react";
import { Plus, Tag, Search, SlidersHorizontal, Edit, Trash2, Calendar } from "lucide-react";
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
import { SimplePagination } from "@/components/common/simple-pagination";
import { ErrorState, EmptyState } from "@/components/shared/api-states";

export const Route = createFileRoute("/categories")({
  head: () => ({ meta: [{ title: "Categories — Billix" }] }),
  component: CategoriesPage,
});

export interface Category {
  id: string;
  business_id: string;
  name: string;
  description?: string | null;
  parent_id?: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

interface CategoryListResponse {
  items: Category[];
  total: number;
}

function CategoriesPage() {
  const queryClient = useQueryClient();
  const { activeBusinessId } = useBusiness();

  // 1. Filter parameters state
  const [page, setPage] = useState(1);
  const [limit] = useState(12);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // 2. Modals state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | null>(null);

  // 3. Form input states
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // 4. Debounce input value changes
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  // 5. Query categories from backend API
  const { data, isLoading, error, refetch } = useBusinessQuery<CategoryListResponse>(
    ["categories", page, limit, debouncedSearch],
    `${API_ENDPOINTS.categories.list}?skip=${(page - 1) * limit}&limit=${limit}${
      debouncedSearch ? `&search_query=${encodeURIComponent(debouncedSearch)}` : ""
    }`,
  );

  // 6. Create category mutation
  const createMutation = useMutation({
    mutationFn: (payload: { name: string; description?: string | null }) => {
      return apiClient<Category>("/api/v1/categories", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      invalidateCache("category:create", queryClient);
      toast.success("Category registered successfully.");
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create category.");
    },
  });

  // 7. Update category mutation
  const updateMutation = useMutation({
    mutationFn: (vars: { id: string; payload: { name: string; description?: string | null } }) => {
      return apiClient<Category>(`/api/v1/categories/${vars.id}`, {
        method: "PATCH",
        body: JSON.stringify(vars.payload),
      });
    },
    onSuccess: () => {
      invalidateCache("category:create", queryClient);
      toast.success("Category updated successfully.");
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update category.");
    },
  });

  // 8. Delete / Deactivate category mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => {
      return apiClient<Category>(`/api/v1/categories/${id}`, {
        method: "DELETE",
      });
    },
    onSuccess: () => {
      invalidateCache("category:create", queryClient);
      toast.success("Category deactivated successfully.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to deactivate category.");
      setIsConfirmOpen(false);
      setDeactivatingId(null);
    },
  });

  const resetForm = () => {
    setFormData({ name: "", description: "" });
    setFormErrors({});
    setSelectedCategory(null);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.name.trim()) {
      errors.name = "Category name is required.";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
      name: formData.name.trim(),
      description: formData.description.trim() || null,
    };

    if (selectedCategory) {
      updateMutation.mutate({ id: selectedCategory.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleEditClick = (c: Category) => {
    setSelectedCategory(c);
    setFormData({
      name: c.name || "",
      description: c.description || "",
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

  // Render skeletons during loading state
  if (isLoading) {
    return <CategoriesSkeleton />;
  }

  // Handle server errors
  if (error) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] items-center justify-center">
          <ErrorState
            title="Failed to load categories"
            description={error.message || "Could not retrieve catalog categories."}
            onRetry={refetch}
          />
        </div>
      </AppShell>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;

  return (
    <AppShell>
      <PageHeader
        title="Categories"
        description="Organise products, set default GST rates and HSN codes."
        actions={
          <Button onClick={handleCreateClick} className="gap-1.5 shadow-sm">
            <Plus className="h-4 w-4" /> Add Category
          </Button>
        }
      />

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search categories…"
            className="h-9 pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="text-xs text-muted-foreground font-medium">Total Categories: {total}</div>
      </div>

      {items.length === 0 ? (
        <EmptyState
          title={search ? "No categories found" : "No categories created yet"}
          description={
            search
              ? "Try adjusting your search criteria."
              : "Create your first product category to organize your inventory item catalog."
          }
          actionText={search ? undefined : "Create First Category"}
          onActionClick={search ? undefined : handleCreateClick}
        />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((c) => (
              <Card key={c.id} className="shadow-sm border transition-all hover:shadow-md">
                <CardContent className="p-5 flex flex-col justify-between h-full">
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div className="grid h-10 w-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                        <Tag className="h-5 w-5" />
                      </div>
                      <Badge variant={c.is_active ? "outline" : "destructive"}>
                        {c.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                    <div className="mt-4 font-display text-lg font-semibold text-foreground">
                      {c.name}
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground line-clamp-2 leading-relaxed min-h-[2rem]">
                      {c.description || "No description provided."}
                    </p>
                  </div>

                  <div className="mt-6 pt-4 border-t space-y-3">
                    <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
                      <Calendar className="h-3 w-3" /> Created{" "}
                      {new Date(c.created_at).toLocaleDateString("en-IN")}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1 gap-1"
                        onClick={() => handleEditClick(c)}
                      >
                        <Edit className="h-3.5 w-3.5" /> Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-destructive hover:text-destructive hover:bg-destructive/10 gap-1"
                        onClick={() => handleDeactivateClick(c.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" /> Deactivate
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <SimplePagination
            total={total}
            page={page}
            pageSize={limit}
            onPageChange={(p) => setPage(p)}
          />
        </>
      )}

      {/* CREATE / EDIT CATEGORY DIALOG */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{selectedCategory ? "Edit Category" : "Add New Category"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div className="space-y-1">
              <Label htmlFor="cat_name">Category Name *</Label>
              <Input
                id="cat_name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Pharmaceuticals, Electronics, Apparel"
              />
              {formErrors.name && <p className="text-xs text-destructive">{formErrors.name}</p>}
            </div>

            <div className="space-y-1">
              <Label htmlFor="cat_desc">Description</Label>
              <Textarea
                id="cat_desc"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Optional description or category details…"
              />
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
                {selectedCategory ? "Save Changes" : "Create Category"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* CONFIRM DEACTIVATION DIALOG */}
      <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Deactivate Category?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm text-muted-foreground">
            Are you sure you want to deactivate this product category? Products associated with this
            category will remain intact.
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
              Deactivate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

function CategoriesSkeleton() {
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

        <div className="h-9 w-64 animate-pulse rounded bg-muted/60" />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="h-48 w-full animate-pulse rounded-xl border bg-card p-5 shadow-sm"
            />
          ))}
        </div>
      </div>
    </AppShell>
  );
}
