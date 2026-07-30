import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { useSignUp } from "@clerk/tanstack-react-start/legacy";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

export const Route = createFileRoute("/register")({
  head: () => ({ meta: [{ title: "Create account — Billix" }] }),
  component: RegisterPage,
});

function RegisterPage() {
  const { isLoaded, signUp, setActive } = useSignUp();

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [businessType, setBusinessType] = useState("");
  const [stateCode, setStateCode] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingVerification, setPendingVerification] = useState(false);
  const [code, setCode] = useState("");

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || !signUp) return;
    setLoading(true);
    setError("");

    const nameParts = fullName.trim().split(" ");
    const firstName = nameParts[0] || "";
    const lastName = nameParts.slice(1).join(" ") || "";

    try {
      await signUp.create({
        emailAddress: email,
        password,
        firstName,
        lastName,
      });

      await signUp.prepareEmailAddressVerification({ strategy: "email_code" });
      setPendingVerification(true);
    } catch (err: unknown) {
      const clerkError = err as { errors?: Array<{ message: string }> };
      const errorMessage =
        clerkError.errors?.[0]?.message || (err as Error)?.message || "Failed to create account.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || !signUp) return;
    setLoading(true);
    setError("");

    try {
      const completeSignUp = await signUp.attemptEmailAddressVerification({
        code,
      });

      if (completeSignUp.status === "complete") {
        if (setActive && completeSignUp.createdSessionId) {
          await setActive({ session: completeSignUp.createdSessionId });
        }
      } else {
        setError("Verification failed or incomplete.");
      }
    } catch (err: unknown) {
      const clerkError = err as { errors?: Array<{ message: string }> };
      const errorMessage =
        clerkError.errors?.[0]?.message ||
        (err as Error)?.message ||
        "Failed to verify email code.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    if (!isLoaded || !signUp) return;
    setLoading(true);
    setError("");

    try {
      await signUp.authenticateWithRedirect({
        strategy: "oauth_google",
        redirectUrl: "/sso-callback",
        redirectUrlComplete: "/dashboard",
      });
    } catch (err: unknown) {
      const clerkError = err as { errors?: Array<{ message: string }> };
      const errorMessage =
        clerkError.errors?.[0]?.message || (err as Error)?.message || "Google Sign-Up failed.";
      setError(errorMessage);
      setLoading(false);
    }
  };

  if (pendingVerification) {
    return (
      <AuthLayout
        title="Verify your email"
        subtitle={`We've sent a 6-digit verification code to ${email}.`}
      >
        <form className="space-y-4" onSubmit={handleVerify}>
          {error && (
            <div className="rounded-lg bg-destructive/15 p-3 text-xs text-destructive font-medium">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="code">Verification Code</Label>
            <Input
              id="code"
              type="text"
              placeholder="123456"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              disabled={loading || !isLoaded}
            />
          </div>
          <Button className="w-full" size="lg" type="submit" disabled={loading || !isLoaded}>
            {loading ? "Verifying..." : "Verify & Continue"}
          </Button>
        </form>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start your 14-day free trial. No card required."
      footer={
        <>
          Already using Billix?{" "}
          <Link to="/login" className="font-semibold text-primary hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSignUp}>
        {error && (
          <div className="rounded-lg bg-destructive/15 p-3 text-xs text-destructive font-medium">
            {error}
          </div>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="fname">Full name</Label>
            <Input
              id="fname"
              placeholder="Rahul Sharma"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              disabled={loading || !isLoaded}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Mobile</Label>
            <Input
              id="phone"
              placeholder="+91 98xxx xxxxx"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              disabled={loading || !isLoaded}
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="business">Business name</Label>
          <Input
            id="business"
            placeholder="Sharma Retail Store"
            value={businessName}
            onChange={(e) => setBusinessName(e.target.value)}
            disabled={loading || !isLoaded}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="type">Business type</Label>
            <Select onValueChange={setBusinessType} disabled={loading || !isLoaded}>
              <SelectTrigger>
                <SelectValue placeholder="Select" />
              </SelectTrigger>
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
            <Select onValueChange={setStateCode} disabled={loading || !isLoaded}>
              <SelectTrigger>
                <SelectValue placeholder="Select" />
              </SelectTrigger>
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
          <Input
            id="email"
            type="email"
            placeholder="you@business.in"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading || !isLoaded}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="Minimum 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading || !isLoaded}
          />
        </div>
        <Button className="w-full" size="lg" type="submit" disabled={loading || !isLoaded}>
          {loading ? "Creating account..." : "Create account"}
        </Button>
        <div className="relative py-2">
          <Separator />
          <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-2 text-xs text-muted-foreground">
            OR
          </span>
        </div>
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={handleGoogleSignUp}
          disabled={loading || !isLoaded}
        >
          Continue with Google
        </Button>
        <p className="text-center text-xs text-muted-foreground">
          By continuing, you agree to Billix's Terms & Privacy Policy.
        </p>
      </form>
    </AuthLayout>
  );
}
