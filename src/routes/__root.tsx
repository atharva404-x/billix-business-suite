import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  useRouterState,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";
import { ClerkProvider, useAuth } from "@clerk/tanstack-react-start";
import { BusinessProvider, useBusiness } from "@/hooks/use-business";
import { OnboardingModal } from "@/components/auth/onboarding-modal";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-foreground">404</h1>
        <h2 className="mt-4 text-xl font-semibold text-foreground">Page not found</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            Go back home
          </Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent({ error }: { error: unknown }) {
  useEffect(() => {
    reportLovableError(error, {
      component: "RootErrorComponent",
    });
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-destructive">Error</h1>
        <h2 className="mt-4 text-xl font-semibold text-foreground">Something went wrong</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          We encountered an unexpected error. Please try reloading the page.
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <button
            onClick={() => window.location.reload()}
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            Reload page
          </button>
          <a
            href="/"
            className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            Go back home
          </a>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Billix — GST Billing, Inventory & Business Management for India" },
      {
        name: "description",
        content:
          "Billix is a modern cloud billing, GST invoicing, inventory and reports platform built for Indian retail, wholesale and SME businesses.",
      },
      { name: "author", content: "Billix" },
      { property: "og:title", content: "Billix — Modern GST Billing & Inventory" },
      {
        property: "og:description",
        content: "All-in-one billing, GST invoicing and inventory suite for Indian businesses.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:site", content: "@Billix" },
    ],
    links: [
      {
        rel: "stylesheet",
        href: appCss,
      },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap",
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <ClerkProvider>
      <QueryClientProvider client={queryClient}>
        <BusinessProvider>
          <RootAuthWrapper />
        </BusinessProvider>
      </QueryClientProvider>
    </ClerkProvider>
  );
}

function RootAuthWrapper() {
  const { isLoaded, userId } = useAuth();
  const { businesses, isLoading: businessLoading } = useBusiness();
  const router = useRouter();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  const isPublicRoute = ["/", "/login", "/register", "/forgot-password", "/sso-callback"].includes(
    pathname,
  );

  useEffect(() => {
    if (!isLoaded) return;

    if (!userId && !isPublicRoute) {
      router.navigate({ to: "/login", replace: true });
    } else if (userId && (pathname === "/login" || pathname === "/register")) {
      router.navigate({ to: "/dashboard", replace: true });
    }
  }, [isLoaded, userId, pathname, isPublicRoute, router]);

  if (!isLoaded && !isPublicRoute) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground animate-pulse">Loading workspace...</div>
      </div>
    );
  }

  if (userId && businessLoading && !isPublicRoute) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground animate-pulse">Loading businesses...</div>
      </div>
    );
  }

  return (
    <>
      <Outlet />
      {userId && !businessLoading && businesses.length === 0 && !isPublicRoute && (
        <OnboardingModal />
      )}
    </>
  );
}
