import { createFileRoute, Link } from "@tanstack/react-router";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const Route = createFileRoute("/register")({
  head: () => ({ meta: [{ title: "Create account — Billix" }] }),
  component: RegisterPage,
});

function RegisterPage() {
  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start your 14-day free trial. No card required."
      footer={<>Already using Billix? <Link to="/login" className="font-semibold text-primary hover:underline">Sign in</Link></>}
    >
      <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="fname">Full name</Label>
            <Input id="fname" placeholder="Rahul Sharma" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Mobile</Label>
            <Input id="phone" placeholder="+91 98xxx xxxxx" />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="business">Business name</Label>
          <Input id="business" placeholder="Sharma Retail Store" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="type">Business type</Label>
            <Select>
              <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="retail">Retail Shop</SelectItem>
                <SelectItem value="medical">Medical Store</SelectItem>
                <SelectItem value="hardware">Hardware</SelectItem>
                <SelectItem value="electrical">Electrical</SelectItem>
                <SelectItem value="garments">Garments</SelectItem>
                <SelectItem value="furniture">Furniture</SelectItem>
                <SelectItem value="wholesale">Wholesale</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="state">State</Label>
            <Select>
              <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="mh">Maharashtra</SelectItem>
                <SelectItem value="ka">Karnataka</SelectItem>
                <SelectItem value="dl">Delhi</SelectItem>
                <SelectItem value="gj">Gujarat</SelectItem>
                <SelectItem value="tn">Tamil Nadu</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Work email</Label>
          <Input id="email" type="email" placeholder="you@business.in" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" placeholder="Minimum 8 characters" />
        </div>
        <Button className="w-full" size="lg" asChild><Link to="/dashboard">Create account</Link></Button>
        <p className="text-center text-xs text-muted-foreground">
          By continuing, you agree to Billix's Terms & Privacy Policy.
        </p>
      </form>
    </AuthLayout>
  );
}