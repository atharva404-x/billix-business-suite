import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

export function SimplePagination({ total = 128, page = 1, pageSize = 10 }: { total?: number; page?: number; pageSize?: number }) {
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  return (
    <div className="mt-4 flex flex-col items-center justify-between gap-3 text-sm sm:flex-row">
      <div className="text-muted-foreground">Showing {from}–{to} of {total}</div>
      <div className="flex items-center gap-1">
        <Button variant="outline" size="sm" className="h-8 gap-1"><ChevronLeft className="h-4 w-4" /> Prev</Button>
        <Button variant="outline" size="sm" className="h-8 w-8 p-0">1</Button>
        <Button size="sm" className="h-8 w-8 p-0">2</Button>
        <Button variant="outline" size="sm" className="h-8 w-8 p-0">3</Button>
        <Button variant="outline" size="sm" className="h-8 gap-1">Next <ChevronRight className="h-4 w-4" /></Button>
      </div>
    </div>
  );
}