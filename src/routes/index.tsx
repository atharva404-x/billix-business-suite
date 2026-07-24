import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  ReceiptText,
  Boxes,
  LineChart,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export const Route = createFileRoute("/")({
  component: Landing,
});

function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link to="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="h-4 w-4" />
          </div>
          <span className="font-display text-lg font-bold tracking-tight">Billix</span>
        </Link>
        <nav className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
          <a href="#features" className="hover:text-foreground">
            Features
          </a>
          <a href="#pricing" className="hover:text-foreground">
            Pricing
          </a>
          <a href="#faq" className="hover:text-foreground">
            Support
          </a>
        </nav>
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost" size="sm">
            <Link to="/login">Sign in</Link>
          </Button>
          <Button asChild size="sm">
            <Link to="/register">Start free</Link>
          </Button>
        </div>
      </header>

      <section className="relative overflow-hidden px-6 pb-24 pt-16 md:pt-24">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1 text-xs">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-success" />
            <span className="text-muted-foreground">
              GST 2.0 compliant · E-invoice ready · Made in India
            </span>
          </div>
          <h1 className="mt-6 font-display text-4xl font-bold leading-[1.05] tracking-tight md:text-6xl">
            Modern billing & inventory for every{" "}
            <span className="text-primary">Indian business.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-muted-foreground">
            Billix helps retail, wholesale, medical and hardware businesses run GST invoices, live
            stock and clear reports — all from one calm workspace.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button asChild size="lg" className="gap-2">
              <Link to="/register">
                Start 14-day free trial <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/dashboard">View live demo</Link>
            </Button>
          </div>
          <div className="mt-4 flex items-center justify-center gap-4 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3 text-success" /> No credit card
            </span>
            <span className="inline-flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3 text-success" /> Cancel anytime
            </span>
          </div>
        </div>

        <div className="mx-auto mt-16 max-w-5xl">
          <div className="rounded-2xl border bg-card p-2 shadow-2xl shadow-primary/10">
            <div className="rounded-xl bg-gradient-to-br from-primary/5 via-accent/40 to-background p-8">
              <div className="grid gap-4 sm:grid-cols-3">
                {[
                  { k: "Revenue", v: "₹12.8L", h: "+12.4% MoM" },
                  { k: "Invoices", v: "1,284", h: "This month" },
                  { k: "Stock value", v: "₹34.2L", h: "Live" },
                ].map((s) => (
                  <Card key={s.k}>
                    <CardContent className="p-4">
                      <div className="text-xs uppercase text-muted-foreground">{s.k}</div>
                      <div className="mt-1 font-display text-2xl font-bold">{s.v}</div>
                      <div className="text-xs text-muted-foreground">{s.h}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="border-t bg-muted/30 px-6 py-24">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center font-display text-3xl font-bold tracking-tight md:text-4xl">
            Everything you need to bill smarter
          </h2>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: ReceiptText,
                t: "GST Invoices",
                d: "HSN, e-invoice, e-way bill and thermal print ready.",
              },
              {
                icon: Boxes,
                t: "Live Inventory",
                d: "Batch, expiry, low-stock alerts across branches.",
              },
              {
                icon: LineChart,
                t: "Sharp Reports",
                d: "GSTR-1, GSTR-3B, sales, purchase and profit views.",
              },
              {
                icon: ShieldCheck,
                t: "Secure Cloud",
                d: "Encrypted backups, role-based access, audit log.",
              },
            ].map((f) => (
              <Card key={f.t}>
                <CardContent className="p-6">
                  <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary">
                    <f.icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-4 font-display font-semibold">{f.t}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{f.d}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t px-6 py-8 text-center text-xs text-muted-foreground">
        © 2026 Billix Technologies Pvt. Ltd. · Made in India
      </footer>
    </div>
  );
}
