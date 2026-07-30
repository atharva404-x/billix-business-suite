import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  ReceiptText,
  Boxes,
  LineChart,
  ShieldCheck,
  Smartphone,
  ChevronDown,
  Building2,
  Users,
  Zap,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/")({
  component: Landing,
});

function Landing() {
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/20 selection:text-primary">
      {/* Top Banner */}
      <div className="bg-primary/10 px-4 py-2 text-center text-xs font-medium text-primary">
        🎉 Billix v2.5 Release: Windows EXE Desktop App & Android Mobile Companion now live!
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-background/80 px-6 py-4 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-md shadow-primary/20 transition-transform group-hover:scale-105">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="font-display text-xl font-bold tracking-tight">Billix</span>
          </Link>
          <nav className="hidden items-center gap-8 text-sm font-medium text-muted-foreground md:flex">
            <a href="#features" className="hover:text-foreground transition-colors">
              Features
            </a>
            <a href="#previews" className="hover:text-foreground transition-colors">
              Live Showcase
            </a>
            <a href="#faq" className="hover:text-foreground transition-colors">
              FAQ
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm" className="font-medium">
              <Link to="/login">Sign in</Link>
            </Button>
            <Button asChild size="sm" className="shadow-sm shadow-primary/20 font-medium">
              <Link to="/register">Start 14-day trial</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 pb-20 pt-16 md:pt-24">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))]" />

        <div className="mx-auto max-w-4xl text-center">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border bg-card/80 px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm shadow-sm">
            <span className="inline-block h-2 w-2 rounded-full bg-success animate-pulse" />
            <span className="text-muted-foreground">
              GST 2.0 Compliant · E-Invoice Ready · Multi-Branch Ready
            </span>
          </div>

          <h1 className="mt-8 font-display text-4xl font-bold leading-[1.08] tracking-tight md:text-6xl">
            Modern GST Billing & Inventory for every{" "}
            <span className="gradient-text">Indian business.</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
            Billix empowers retail, wholesale, medical, and hardware enterprises with fast GST
            billing, live stock tracking, and automated GSTR-1 tax compliance from one calm
            workspace.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button
              asChild
              size="lg"
              className="h-12 px-8 text-base shadow-md shadow-primary/20 gap-2"
            >
              <Link to="/register">
                Start 14-day free trial <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="h-12 px-8 text-base">
              <Link to="/dashboard">Explore Live Workspace</Link>
            </Button>
          </div>

          <div className="mt-6 flex items-center justify-center gap-6 text-xs font-medium text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> No credit card required
            </span>
            <span className="inline-flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> Windows EXE & Android
            </span>
            <span className="inline-flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> Instant Setup
            </span>
          </div>
        </div>

        {/* Hero Interactive App Preview Card */}
        <div id="previews" className="mx-auto mt-16 max-w-5xl">
          <div className="rounded-2xl border bg-card p-3 shadow-2xl shadow-primary/10">
            <div className="rounded-xl border bg-background p-6">
              <div className="flex items-center justify-between border-b pb-4 mb-6">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-destructive/60" />
                  <div className="h-3 w-3 rounded-full bg-warning/60" />
                  <div className="h-3 w-3 rounded-full bg-success/60" />
                  <span className="ml-2 text-xs font-mono text-muted-foreground">
                    app.billix.in/dashboard
                  </span>
                </div>
                <Badge variant="outline" className="text-xs font-medium">
                  Live BI Dashboard
                </Badge>
              </div>

              <div className="grid gap-4 sm:grid-cols-4">
                {[
                  { k: "Total Revenue", v: "₹18,42,500", h: "+14.2% MoM", color: "text-primary" },
                  {
                    k: "Invoices Raised",
                    v: "1,482",
                    h: "100% Tax Compliant",
                    color: "text-success",
                  },
                  {
                    k: "Stock Value",
                    v: "₹42,80,000",
                    h: "Active Stock",
                    color: "text-foreground",
                  },
                  { k: "GST Collected", v: "₹3,31,650", h: "GSTR-1 Ready", color: "text-primary" },
                ].map((s) => (
                  <div key={s.k} className="rounded-xl border bg-card p-4 shadow-sm">
                    <div className="text-xs font-medium text-muted-foreground">{s.k}</div>
                    <div className={`mt-1 font-display text-2xl font-bold ${s.color}`}>{s.v}</div>
                    <div className="mt-1 text-[11px] text-muted-foreground">{s.h}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section id="features" className="border-t bg-muted/20 px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <div className="text-center max-w-2xl mx-auto">
            <Badge variant="secondary" className="mb-3">
              Engineered for Speed
            </Badge>
            <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
              Everything required to run a high-volume business
            </h2>
            <p className="mt-3 text-muted-foreground">
              Built specifically for Indian retail, medical, hardware, and wholesale billing
              requirements.
            </p>
          </div>

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: ReceiptText,
                title: "GST Invoicing Engine",
                desc: "Generate e-way bills, thermal receipts, and A4 GST tax invoices with HSN auto-fill and multi-rate tax breakdowns.",
              },
              {
                icon: Boxes,
                title: "Live Inventory Control",
                desc: "Track batch numbers, expiration dates, stock valuation, and receive automated low-stock reorder warnings.",
              },
              {
                icon: LineChart,
                title: "GSTR-1 & BI Analytics",
                desc: "One-click GSTR-1, GSTR-3B tax export ledgers, top product performance metrics, and sales trend intelligence.",
              },
              {
                icon: Building2,
                title: "Multi-Branch Workspace",
                desc: "Manage multiple business locations or entities seamlessly with strict data isolation and instant switching.",
              },
              {
                icon: Smartphone,
                title: "Desktop & Mobile Sync",
                desc: "Native Windows EXE desktop application paired with an Android mobile app for billing on counter or on the move.",
              },
              {
                icon: ShieldCheck,
                title: "Bank-Grade Security",
                desc: "Row-level tenant security, encrypted daily automated database backups, and fine-grained audit log trails.",
              },
            ].map((f) => (
              <Card key={f.title} className="shadow-sm border hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="grid h-12 w-12 place-items-center rounded-xl bg-primary/10 text-primary">
                    <f.icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-5 font-display text-lg font-bold">{f.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="border-t px-6 py-24 bg-background">
        <div className="mx-auto max-w-4xl">
          <div className="text-center">
            <Badge variant="secondary" className="mb-3">
              Frequently Asked Questions
            </Badge>
            <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
              Got questions? We've got answers.
            </h2>
          </div>

          <div className="mt-12 space-y-4">
            {[
              {
                q: "Is Billix fully compliant with Indian GST laws?",
                a: "Yes! Billix supports 100% compliant GSTR-1, GSTR-3B ledgers, CGST, SGST, IGST tax splits, HSN code indexing, and e-way bill exports.",
              },
              {
                q: "Can I use Billix on a Windows Desktop EXE and Android?",
                a: "Absolutely. Billix is engineered to run seamlessly as a native Windows EXE desktop application for high-speed counter billing and as an Android app for mobile store managers.",
              },
              {
                q: "Does Billix support thermal invoice printers and barcode scanners?",
                a: "Yes, Billix integrates directly with thermal receipt printers (2-inch and 3-inch), standard A4 printers, and USB/Bluetooth barcode scanners.",
              },
              {
                q: "How does multi-business switching work?",
                a: "You can create and manage multiple businesses under one account. Switching between businesses instantly updates all queries, invoices, inventory, and reports with zero cross-tenant leakage.",
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className="rounded-xl border bg-card overflow-hidden transition-colors"
              >
                <button
                  onClick={() => toggleFaq(idx)}
                  className="flex w-full items-center justify-between p-5 text-left font-display font-semibold text-base"
                >
                  <span>{item.q}</span>
                  <ChevronDown
                    className={`h-5 w-5 text-muted-foreground transition-transform ${
                      openFaq === idx ? "rotate-180 text-primary" : ""
                    }`}
                  />
                </button>
                {openFaq === idx && (
                  <div className="px-5 pb-5 text-sm text-muted-foreground leading-relaxed border-t pt-3">
                    {item.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer Section */}
      <section className="border-t bg-primary/5 px-6 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            Ready to upgrade your GST billing workflow?
          </h2>
          <p className="mt-4 text-muted-foreground">
            Join thousands of Indian business owners managing billing, stock, and GST from one
            modern workspace.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button
              asChild
              size="lg"
              className="h-12 px-8 text-base shadow-md shadow-primary/20 gap-2"
            >
              <Link to="/register">
                Start 14-day free trial <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-background px-6 py-10 text-xs text-muted-foreground">
        <div className="mx-auto max-w-6xl flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="grid h-6 w-6 place-items-center rounded bg-primary text-primary-foreground text-xs font-bold">
              B
            </div>
            <span className="font-display font-bold text-foreground">Billix Technologies</span>
          </div>
          <div>© 2026 Billix Technologies Pvt. Ltd. · Made with ❤️ in India</div>
          <div className="flex gap-4">
            <Link to="/login" className="hover:text-foreground">
              Sign In
            </Link>
            <Link to="/register" className="hover:text-foreground">
              Register
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
