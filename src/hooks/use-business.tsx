import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuth } from "@clerk/clerk-react";
import { useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

export interface BusinessProfile {
  id: string;
  business_name: string;
  gstin?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  pincode?: string | null;
  phone?: string | null;
  email?: string | null;
}

interface BusinessContextType {
  activeBusiness: BusinessProfile | null;
  activeBusinessId: string | null;
  activeBusinessName: string | null;
  role: string | null;
  isLoading: boolean;
  businesses: BusinessProfile[];
  switchBusiness: (id: string) => void;
  refreshBusinesses: () => Promise<void>;
  createBusiness: (data: {
    business_name: string;
    business_type: string;
    gstin?: string;
    email?: string;
    phone?: string;
    address?: string;
    currency?: string;
    timezone?: string;
    financial_year?: number;
  }) => Promise<BusinessProfile>;
}

const BusinessContext = createContext<BusinessContextType | undefined>(undefined);

export function BusinessProvider({ children }: { children: React.ReactNode }) {
  const { isLoaded: authLoaded, userId } = useAuth();
  const queryClient = useQueryClient();

  const [businesses, setBusinesses] = useState<BusinessProfile[]>([]);
  const [activeBusiness, setActiveBusiness] = useState<BusinessProfile | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchBusinesses = useCallback(async () => {
    if (!userId) {
      setBusinesses([]);
      setActiveBusiness(null);
      setRole(null);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const res = await apiClient<{ items: BusinessProfile[]; total: number }>(
        "/api/v1/business-profiles",
      );
      const items = res.items || [];
      setBusinesses(items);

      if (items.length > 0) {
        const savedId = localStorage.getItem("active_business_id");
        const found = items.find((b) => b.id === savedId);
        const selected = found || items[0];

        setActiveBusiness(selected);
        localStorage.setItem("active_business_id", selected.id);
        localStorage.setItem("active_business_name", selected.business_name);

        // Default membership role to Owner as user is loaded under list_by_user
        setRole("owner");
        localStorage.setItem("active_business_role", "owner");
      } else {
        setActiveBusiness(null);
        setRole(null);
        localStorage.removeItem("active_business_id");
        localStorage.removeItem("active_business_name");
        localStorage.removeItem("active_business_role");
      }
    } catch (e: unknown) {
      const err = e as Error;
      toast.error(`Failed to load business profiles: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (authLoaded) {
      fetchBusinesses();
    }
  }, [authLoaded, fetchBusinesses]);

  const switchBusiness = (id: string) => {
    const selected = businesses.find((b) => b.id === id);
    if (!selected) return;

    setActiveBusiness(selected);
    localStorage.setItem("active_business_id", selected.id);
    localStorage.setItem("active_business_name", selected.business_name);
    setRole("owner");
    localStorage.setItem("active_business_role", "owner");

    toast.success(`Switched to business: ${selected.business_name}`);

    // Invalidate and refresh React Query cache queries
    queryClient.invalidateQueries();
  };

  const createBusiness = async (data: {
    business_name: string;
    business_type: string;
    gstin?: string;
    email?: string;
    phone?: string;
    address?: string;
    currency?: string;
    timezone?: string;
    financial_year?: number;
  }) => {
    try {
      setIsLoading(true);
      // 1. POST /api/v1/business-profiles
      const profile = await apiClient<BusinessProfile>("/api/v1/business-profiles", {
        method: "POST",
        body: JSON.stringify({
          business_name: data.business_name,
          gstin: data.gstin || null,
          address: data.address || null,
          email: data.email || null,
          phone: data.phone || null,
        }),
      });

      // 2. PATCH settings for currency, timezone, financial year
      await apiClient(`/api/v1/business-profiles/${profile.id}/settings`, {
        method: "PATCH",
        body: JSON.stringify({
          company_name: data.business_name,
          company_address: data.address || null,
          gstin: data.gstin || null,
          currency: data.currency || "INR",
          timezone: data.timezone || "Asia/Kolkata",
          financial_year_start: data.financial_year || 4, // 4 = April
        }),
      });

      // 3. PATCH preferences for business type
      await apiClient(`/api/v1/business-profiles/${profile.id}/preferences`, {
        method: "PATCH",
        body: JSON.stringify({
          report_preferences: {
            business_type: data.business_type,
          },
        }),
      });

      toast.success(`Business ${data.business_name} created successfully!`);

      // Refresh profiles list and auto-select new business
      await fetchBusinesses();
      return profile;
    } catch (e: unknown) {
      const err = e as Error;
      toast.error(`Failed to create business: ${err.message}`);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <BusinessContext.Provider
      value={{
        activeBusiness,
        activeBusinessId: activeBusiness?.id || null,
        activeBusinessName: activeBusiness?.business_name || null,
        role,
        isLoading,
        businesses,
        switchBusiness,
        refreshBusinesses: fetchBusinesses,
        createBusiness,
      }}
    >
      {children}
    </BusinessContext.Provider>
  );
}

export function useBusiness() {
  const context = useContext(BusinessContext);
  if (context === undefined) {
    throw new Error("useBusiness must be used within a BusinessProvider");
  }
  return context;
}
