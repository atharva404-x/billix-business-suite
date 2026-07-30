export const API_ENDPOINTS = {
  auth: {
    me: "/api/v1/users/me",
  },
  business: {
    list: "/api/v1/business-profiles",
    create: "/api/v1/business-profiles",
    detail: (id: string) => `/api/v1/business-profiles/${id}`,
    settings: (id: string) => `/api/v1/business-profiles/${id}/settings`,
    preferences: (id: string) => `/api/v1/business-profiles/${id}/preferences`,
  },
  dashboard: "/api/v1/reports/dashboard",
  reports: {
    sales: "/api/v1/reports/sales",
    customers: "/api/v1/reports/customers",
    products: "/api/v1/reports/products",
    payments: "/api/v1/reports/payments",
    inventory: "/api/v1/reports/inventory",
  },
  customers: {
    list: "/api/v1/customers",
    create: "/api/v1/customers",
    detail: (id: string) => `/api/v1/customers/${id}`,
  },
  products: {
    list: "/api/v1/products",
    create: "/api/v1/products",
    detail: (id: string) => `/api/v1/products/${id}`,
  },
  invoices: {
    list: "/api/v1/invoices",
    create: "/api/v1/invoices",
    detail: (id: string) => `/api/v1/invoices/${id}`,
  },
} as const;
