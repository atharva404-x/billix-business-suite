import { createFileRoute } from "@tanstack/react-router";
import { Plus, Tag } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { categories } from "@/lib/mock-data";

export const Route = createFileRoute("/categories")({
  head: () => ({ meta: [{ title: "Categories — Billix" }] }),
  component: CategoriesPage,
});

function CategoriesPage() {
  return (
    <AppShell>
      <PageHeader
        title="Categories"
        description="Organise products, set default GST rates and HSN codes."
        actions={<Button className="gap-1.5"><Plus className="h-4 w-4" /> Add Category</Button>}
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categories.map((c) => (
          <Card key={c.id}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                  <Tag className="h-5 w-5" />
                </div>
                <span className="rounded-full bg-muted px-2 py-0.5 text-xs">GST {c.gstDefault}</span>
              </div>
              <div className="mt-4 font-display text-lg font-semibold">{c.name}</div>
              <div className="text-xs text-muted-foreground">{c.products} products</div>
              <div className="mt-4 flex gap-2">
                <Button size="sm" variant="outline" className="flex-1">Edit</Button>
                <Button size="sm" variant="ghost" className="flex-1">View</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}