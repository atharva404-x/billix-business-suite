import { Link } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { Sparkles, ShieldCheck, Zap, BadgeIndianRupee } from "lucide-react";

export function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden overflow-hidden bg-gradient-to-br from-primary via-primary to-[color-mix(in_oklab,var(--primary),black_20%)] p-10 text-primary-foreground lg:flex lg:flex-col lg:justify-between">
        <div className="absolute inset-0 opacity-20 [background:radial-gradient(circle_at_20%_10%,white,transparent_40%),radial-gradient(circle_at_80%_80%,white,transparent_40%)]" />
        <Link to="/" className="relative flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-lg bg-white/15 backdrop-blur">
            <Sparkles className="h-5 w-5" />
          </div>
          <span className="font-display text-xl font-bold tracking-tight">Billix</span>
        </Link>
        <div className="relative max-w-md">
          <h2 className="font-display text-4xl font-bold leading-tight">
            Run your entire business, from one calm dashboard.
          </h2>
          <p className="mt-4 text-primary-foreground/80">
            GST-ready invoicing, live inventory and clear reports — built for Indian retail, wholesale and SMEs.
          </p>
          <div className="mt-8 grid gap-3 text-sm">
            <div className="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur">
              <BadgeIndianRupee className="h-4 w-4 shrink-0" /> GST invoices, e-way bills & HSN in one click
            </div>
            <div className="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur">
              <Zap className="h-4 w-4 shrink-0" /> Fast billing on desktop, tablet and mobile
            </div>
            <div className="flex items-center gap-3 rounded-xl bg-white/10 p-3 backdrop-blur">
              <ShieldCheck className="h-4 w-4 shrink-0" /> Bank-grade security, daily encrypted backups
            </div>
          </div>
        </div>
        <div className="relative text-xs text-primary-foreground/70">
          Trusted by 12,000+ Indian businesses across retail, medical, hardware & wholesale.
        </div>
      </div>
      <div className="flex flex-col justify-center px-6 py-10 sm:px-10 lg:px-16">
        <div className="mx-auto w-full max-w-md">
          <Link to="/" className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-display text-lg font-bold">Billix</span>
          </Link>
          <h1 className="font-display text-3xl font-bold tracking-tight">{title}</h1>
          {subtitle && <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>}
          <div className="mt-8">{children}</div>
          {footer && <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>}
        </div>
      </div>
    </div>
  );
}