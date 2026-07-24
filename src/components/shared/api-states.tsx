import React from "react";
import { Loader2, AlertCircle, Inbox, RefreshCw, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = "Loading data...", className = "" }: LoadingStateProps) {
  return (
    <div
      className={`flex min-h-[240px] w-full flex-col items-center justify-center gap-3 p-6 ${className}`}
    >
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="text-sm font-medium text-muted-foreground animate-pulse">{message}</p>
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Failed to load details",
  description = "An error occurred while fetching information from the servers.",
  onRetry,
  className = "",
}: ErrorStateProps) {
  return (
    <div
      className={`flex min-h-[240px] w-full flex-col items-center justify-center text-center p-6 ${className}`}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive mb-4">
        <AlertCircle className="h-6 w-6" />
      </div>
      <h3 className="text-base font-bold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-4 leading-relaxed">{description}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" size="sm" className="gap-2">
          <RefreshCw className="h-3.5 w-3.5" /> Retry Request
        </Button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  onActionClick?: () => void;
  className?: string;
}

export function EmptyState({
  title = "No items found",
  description = "Get started by adding your first record to the workspace.",
  actionText,
  onActionClick,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex min-h-[320px] w-full flex-col items-center justify-center text-center p-8 border border-dashed rounded-xl bg-muted/20 ${className}`}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground mb-4">
        <Inbox className="h-6 w-6" />
      </div>
      <h3 className="text-base font-bold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-6 leading-relaxed">{description}</p>
      {actionText && onActionClick && (
        <Button onClick={onActionClick} size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" /> {actionText}
        </Button>
      )}
    </div>
  );
}
