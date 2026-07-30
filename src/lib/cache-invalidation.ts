import { QueryClient } from "@tanstack/react-query";

export type InvalidationAction =
  | "customer:create"
  | "customer:update"
  | "customer:delete"
  | "invoice:create"
  | "invoice:cancel"
  | "invoice:delete"
  | "product:create"
  | "product:update"
  | "product:delete";

export const CACHE_KEYS = {
  dashboard: ["dashboard"],
  reports: ["reports"],
  invoices: ["invoices"],
  customers: ["customers"],
  products: ["products"],
} as const;

export function invalidateCache(action: InvalidationAction, queryClient: QueryClient) {
  switch (action) {
    case "customer:create":
    case "customer:update":
    case "customer:delete":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.customers });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      break;

    case "invoice:create":
    case "invoice:cancel":
    case "invoice:delete":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.reports });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.invoices });
      break;

    case "product:create":
    case "product:update":
    case "product:delete":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.products });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      break;

    default:
      break;
  }
}
