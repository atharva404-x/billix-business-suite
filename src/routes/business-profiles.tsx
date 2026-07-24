import { createFileRoute } from "@tanstack/react-router";
import { Building2, Plus, Check } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/common/status-badge";
import { businessProfiles } from "@/lib/mock-data";

export const Route = createFileRoute("/business-profiles")({
  head: () => ({ meta: [{ title: "Business Profiles — Billix" }] }),
  component: BusinessProfilesPage,
});

function BusinessProfilesPage() {
  return (
    <AppShell>
      <PageHeader
        title="Business Profiles"
        description="Manage multiple GSTINs, branches and outlets from one login."
        actions={
          <Button className="gap-1.5">
            <Plus className="h-4 w-4" /> Add Business
          </Button>
        }
      />
      <div className="grid gap-4 md:grid-cols-2">
        {businessProfiles.map((b) => (
          <Card key={b.id} className="overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 min-w-0">
                  <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary">
                    <Building2 className="h-6 w-6" />
                  </div>
                  <div className="min-w-0">
                    <div className="font-display text-lg font-semibold">{b.name}</div>
                    <div className="text-xs text-muted-foreground">
                      GSTIN {b.gstin} · {b.city}
                    </div>
                  </div>
                </div>
                <StatusBadge status={b.active ? "Active" : "Inactive"} />
              </div>
              <div className="mt-6 flex items-center gap-2">
                {b.active ? (
                  <Button size="sm" variant="secondary" className="gap-1.5" disabled>
                    <Check className="h-4 w-4" /> Current
                  </Button>
                ) : (
                  <Button size="sm">Switch to this</Button>
                )}
                <Button size="sm" variant="outline">
                  Edit
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        <button className="flex min-h-[168px] items-center justify-center rounded-xl border border-dashed bg-card text-sm text-muted-foreground hover:border-primary hover:text-primary">
          <span className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> Add another business
          </span>
        </button>
      </div>
    </AppShell>
  );
}
