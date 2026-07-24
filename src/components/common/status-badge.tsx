import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const map: Record<string, string> = {
  Paid: "bg-success/10 text-success border-success/20",
  Pending: "bg-warning/15 text-warning-foreground border-warning/30",
  Overdue: "bg-destructive/10 text-destructive border-destructive/20",
  Draft: "bg-muted text-muted-foreground border-border",
  Active: "bg-success/10 text-success border-success/20",
  Inactive: "bg-muted text-muted-foreground border-border",
  "In Stock": "bg-success/10 text-success border-success/20",
  "Low Stock": "bg-warning/15 text-warning-foreground border-warning/30",
  "Out of Stock": "bg-destructive/10 text-destructive border-destructive/20",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge variant="outline" className={cn("rounded-full font-medium", map[status] ?? "")}>
      <span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-current opacity-70" />
      {status}
    </Badge>
  );
}
