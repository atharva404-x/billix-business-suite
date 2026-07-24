import { QueryClient } from "@tanstack/react-query";

export type InvalidationAction =
  | "customer:create"
  | "customer:update"
  | "customer:delete"
  | "invoice:create"
  | "invoice:cancel"
  | "product:create"
  | "product:update"
  | "product:delete"
  | "inventory:adjust"
  | "category:create"
  | "supplier:create"
  | "supplier:update"
  | "supplier:delete";

export const CACHE_KEYS = {
  dashboard: ["dashboard"],
  reports: ["reports"],
  invoices: ["invoices"],
  customers: ["customers"],
  products: ["products"],
  categories: ["categories"],
  suppliers: ["suppliers"],
  inventory: ["inventory"],
} as const;

export function invalidateCache(action: InvalidationAction, queryClient: QueryClient) {
  switch (action) {
    case "customer:create":
    case "customer:update":
    case "customer:delete":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.customers });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      break;

    case "supplier:create":
    case "supplier:update":
    case "supplier:delete":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.suppliers });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      break;

    case "invoice:create":
    case "invoice:cancel":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.reports });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.invoices });
      break;

    case "product:create":
    case "product:update":
    case "product:delete":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.products });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.inventory });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      break;

    case "inventory:adjust":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.inventory });
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.dashboard });
      break;

    case "category:create":
      queryClient.invalidateQueries({ queryKey: CACHE_KEYS.categories });
      break;

    default:
      break;
  }
}
