export function ChartPlaceholder({ height = 260, label = "Revenue trend" }: { height?: number; label?: string }) {
  const bars = [40, 65, 52, 78, 60, 90, 72, 84, 96, 70, 88, 100];
  return (
    <div className="w-full">
      <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span>Last 12 months</span>
      </div>
      <div className="flex items-end gap-2 rounded-lg bg-muted/40 p-4" style={{ height }}>
        {bars.map((h, i) => (
          <div key={i} className="flex-1">
            <div
              className="w-full rounded-md bg-gradient-to-t from-primary/60 to-primary/90 transition-all hover:from-primary hover:to-primary"
              style={{ height: `${h}%` }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}