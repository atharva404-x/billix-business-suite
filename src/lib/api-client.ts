import { toast } from "sonner";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

interface ClerkGlobal {
  session?: {
    getToken: () => Promise<string | null>;
  };
}

export async function apiClient<T = unknown>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { params, headers: customHeaders, ...customOptions } = options;

  const headers = new Headers(customHeaders);

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  let activeBusinessId: string | null = null;
  if (typeof window !== "undefined") {
    activeBusinessId = localStorage.getItem("active_business_id");
    if (activeBusinessId) {
      headers.set("X-Business-ID", activeBusinessId);
    }
  }

  // Dynamically fetch Clerk JWT token on client-side if not explicitly provided
  if (typeof window !== "undefined" && !headers.has("Authorization")) {
    let clerkObj = (window as unknown as { Clerk?: ClerkGlobal }).Clerk;

    // Wait briefly if Clerk JS is initializing
    let attempts = 0;
    while (!clerkObj && attempts < 10) {
      await new Promise((resolve) => setTimeout(resolve, 50));
      clerkObj = (window as unknown as { Clerk?: ClerkGlobal }).Clerk;
      attempts++;
    }

    if (clerkObj?.session) {
      try {
        const token = await clerkObj.session.getToken();
        if (token) {
          headers.set("Authorization", `Bearer ${token}`);
        }
      } catch (e) {
        console.warn("Failed to retrieve Clerk JWT token:", e);
      }
    }
  }

  let url = `${BASE_URL}${endpoint}`;
  const urlParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        urlParams.append(key, String(val));
      }
    });
  }

  // Auto-inject business_id query param if available and not already provided
  if (activeBusinessId && !urlParams.has("business_id")) {
    urlParams.append("business_id", activeBusinessId);
  }

  const queryString = urlParams.toString();
  if (queryString) {
    url += `?${queryString}`;
  }

  const authHeader = headers.get("Authorization");
  const hasAuthHeader = !!authHeader;
  const tokenLength = authHeader ? authHeader.replace(/^Bearer\s+/, "").length : 0;

  console.log("[API CLIENT REQUEST]", {
    url,
    authHeaderPresent: hasAuthHeader ? "YES" : "NO",
    tokenLength,
  });

  try {
    const response = await fetch(url, {
      ...customOptions,
      headers,
    });

    const responseClone = response.clone();
    const responseBodyText = await responseClone.text();
    console.log("[API CLIENT RESPONSE]", {
      status: response.status,
      responseBody: responseBodyText,
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorDetail = "";
      try {
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || errorJson.message || "";
      } catch {
        errorDetail = errorText;
      }

      // Intercept SQL stack traces or database engine details
      const sqlKeywords = [
        "sql",
        "relation",
        "foreign key",
        "unique constraint",
        "psycopg",
        "sqlalchemy",
        "postgres",
      ];
      const containsSqlError = sqlKeywords.some((k) => errorDetail.toLowerCase().includes(k));
      if (containsSqlError) {
        errorDetail = "A database integrity constraint occurred. Please verify your fields.";
      }

      // Global response status code interceptor
      let userFriendlyMsg = "";
      switch (response.status) {
        case 400:
          userFriendlyMsg = errorDetail || "Bad Request. Please verify the submitted data.";
          break;
        case 401:
          userFriendlyMsg = "Session expired. Please sign in again.";
          break;
        case 403:
          userFriendlyMsg = "Access denied. You do not have permissions for this action.";
          break;
        case 404:
          userFriendlyMsg = errorDetail || "Requested resource could not be found.";
          break;
        case 409:
          userFriendlyMsg = errorDetail || "A conflict occurred (e.g. duplicate resource).";
          break;
        case 422:
          userFriendlyMsg = "Input validation failed. Please check your form fields.";
          break;
        case 429:
          userFriendlyMsg = "Too many requests. Please slow down and try again later.";
          break;
        case 500:
        case 502:
        case 503:
          userFriendlyMsg = "An internal server error occurred. Please contact support.";
          break;
        default:
          userFriendlyMsg = errorDetail || "An unexpected error occurred.";
          break;
      }

      // Avoid displaying redundant alerts for background checks or normal redirection triggers
      if (response.status !== 401 && response.status !== 404) {
        toast.error(userFriendlyMsg);
      }

      throw new Error(userFriendlyMsg);
    }

    // Try parsing as JSON, fallback to text if empty response
    const text = await response.text();
    return text ? (JSON.parse(text) as T) : ({} as T);
  } catch (e: unknown) {
    const err = e as Error;
    if (err.message && !err.message.includes("abort") && !err.message.includes("Session expired")) {
      console.error("[API Client Error]:", err.message);
    }
    throw err;
  }
}
