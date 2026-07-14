import { Search, SlidersHorizontal, Download } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { ReactNode } from "react";

export function DataToolbar({ placeholder = "Search…", right }: { placeholder?: string; right?: ReactNode }) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 sm:flex sm:justify-between">
      <div className="relative min-w-0 sm:max-w-sm sm:flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder={placeholder} className="h-9 pl-9" />
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Button variant="outline" size="sm" className="gap-1.5">
          <SlidersHorizontal className="h-4 w-4" /> <span className="hidden sm:inline">Filter</span>
        </Button>
        <Button variant="outline" size="sm" className="gap-1.5">
          <Download className="h-4 w-4" /> <span className="hidden sm:inline">Export</span>
        </Button>
        {right}
      </div>
    </div>
  );
}