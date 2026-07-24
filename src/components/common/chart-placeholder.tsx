export interface ChartSalesItem {
  period: string;
  total_sales: number;
}

export function ChartPlaceholder({
  height = 260,
  label = "Revenue trend",
  data = [],
}: {
  height?: number;
  label?: string;
  data?: ChartSalesItem[];
}) {
  const maxSales = data.length > 0 ? Math.max(...data.map((d) => d.total_sales), 0) : 0;

  // Render a clean fallback if there's no data
  if (data.length === 0) {
    return (
      <div
        className="flex w-full items-center justify-center rounded-lg border border-dashed p-4 text-xs text-muted-foreground"
        style={{ height }}
      >
        No sales data available for this period.
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span>Monthly Sales History</span>
      </div>
      <div className="flex items-end gap-2 rounded-lg bg-muted/40 p-4" style={{ height }}>
        {data.map((item, i) => {
          const percent = maxSales > 0 ? (item.total_sales / maxSales) * 100 : 0;
          return (
            <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
              {/* Tooltip */}
              <span className="pointer-events-none absolute bottom-full mb-1 left-1/2 -translate-x-1/2 scale-0 group-hover:scale-100 transition-all rounded bg-popover px-2 py-1 text-[10px] text-popover-foreground shadow-md whitespace-nowrap z-10 border">
                {item.period}: ₹{item.total_sales.toLocaleString("en-IN")}
              </span>
              <div
                className="w-full rounded-md bg-gradient-to-t from-primary/60 to-primary/90 transition-all hover:from-primary hover:to-primary"
                style={{ height: `${Math.max(percent, 4)}%` }} // Minimum 4% so even small numbers are visible
              />
              <span className="text-[9px] text-muted-foreground hidden sm:block truncate w-full text-center">
                {item.period.split("-")[1] || item.period}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
