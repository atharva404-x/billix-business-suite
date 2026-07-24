import {
  useQuery,
  useMutation,
  UseQueryOptions,
  UseMutationOptions,
  QueryKey,
} from "@tanstack/react-query";
import { useBusiness } from "@/hooks/use-business";
import { apiClient } from "@/lib/api-client";

export function useApi() {
  return { apiClient };
}

export function useAuthenticatedQuery<TData = unknown, TError = Error>(
  queryKey: QueryKey,
  endpoint: string,
  options?: Omit<UseQueryOptions<TData, TError, TData, QueryKey>, "queryKey" | "queryFn">,
) {
  return useQuery<TData, TError, TData, QueryKey>({
    ...options,
    queryKey,
    queryFn: () => apiClient<TData>(endpoint),
  });
}

export function useAuthenticatedMutation<TData = unknown, TError = Error, TVariables = void>(
  endpoint: string,
  options?: UseMutationOptions<TData, TError, TVariables>,
  method: "POST" | "PUT" | "PATCH" | "DELETE" = "POST",
) {
  return useMutation<TData, TError, TVariables>({
    ...options,
    mutationFn: (variables) => {
      return apiClient<TData>(endpoint, {
        method,
        body: variables ? JSON.stringify(variables) : undefined,
      });
    },
  });
}

export function useBusinessQuery<TData = unknown, TError = Error>(
  queryKey: QueryKey,
  endpoint: string,
  options?: Omit<UseQueryOptions<TData, TError, TData, QueryKey>, "queryKey" | "queryFn">,
) {
  const { activeBusinessId } = useBusiness();
  return useQuery<TData, TError, TData, QueryKey>({
    ...options,
    queryKey: [...queryKey, activeBusinessId],
    queryFn: () => apiClient<TData>(endpoint),
    enabled: !!activeBusinessId && options?.enabled !== false,
  });
}

export function useBusinessMutation<TData = unknown, TError = Error, TVariables = void>(
  endpoint: string,
  options?: UseMutationOptions<TData, TError, TVariables>,
  method: "POST" | "PUT" | "PATCH" | "DELETE" = "POST",
) {
  const { activeBusinessId } = useBusiness();
  return useMutation<TData, TError, TVariables>({
    ...options,
    mutationFn: (variables) => {
      if (!activeBusinessId) {
        throw new Error("No active business selected.");
      }
      return apiClient<TData>(endpoint, {
        method,
        body: variables ? JSON.stringify(variables) : undefined,
      });
    },
  });
}
