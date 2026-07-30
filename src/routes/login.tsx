import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { useSignIn } from "@clerk/tanstack-react-start/legacy";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Sign in — Billix" }] }),
  component: LoginPage,
});

function LoginPage() {
  const { isLoaded, signIn, setActive } = useSignIn();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || !signIn) return;
    setLoading(true);
    setError("");

    try {
      const result = await signIn.create({
        identifier: email,
        password,
      });

      if (result.status === "complete") {
        if (setActive && result.createdSessionId) {
          await setActive({ session: result.createdSessionId });
        }
      } else {
        setError("MFA or additional verification required.");
      }
    } catch (err: unknown) {
      const clerkError = err as {
        errors?: Array<{ message: string; code?: string; longMessage?: string }>;
      };
      const errorMessage =
        clerkError.errors?.[0]?.message ||
        (err as Error)?.message ||
        "Failed to sign in. Please check your credentials.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    if (!isLoaded || !signIn) return;
    setLoading(true);
    setError("");

    try {
      await signIn.authenticateWithRedirect({
        strategy: "oauth_google",
        redirectUrl: "/sso-callback",
        redirectUrlComplete: "/dashboard",
      });
    } catch (err: unknown) {
      const clerkError = err as { errors?: Array<{ message: string }> };
      const errorMessage =
        clerkError.errors?.[0]?.message || (err as Error)?.message || "Google Sign-In failed.";
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to continue to your Billix workspace."
      footer={
        <>
          New to Billix?{" "}
          <Link to="/register" className="font-semibold text-primary hover:underline">
            Create an account
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSignIn}>
        {error && (
          <div className="rounded-lg bg-destructive/15 p-3 text-xs text-destructive font-medium">
            {error}
          </div>
        )}
        <div className="space-y-2">
          <Label htmlFor="email">Email address</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@business.in"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading || !isLoaded}
          />
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <Link
              to="/forgot-password"
              className="text-xs font-medium text-primary hover:underline"
            >
              Forgot?
            </Link>
          </div>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading || !isLoaded}
          />
        </div>
        <div className="flex items-center gap-2">
          <Checkbox id="remember" disabled={loading || !isLoaded} />
          <Label htmlFor="remember" className="text-sm font-normal text-muted-foreground">
            Keep me signed in for 30 days
          </Label>
        </div>
        <Button className="w-full" size="lg" type="submit" disabled={loading || !isLoaded}>
          {loading ? "Signing in..." : "Sign in"}
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
          onClick={handleGoogleSignIn}
          disabled={loading || !isLoaded}
        >
          Continue with Google
        </Button>
      </form>
    </AuthLayout>
  );
}
