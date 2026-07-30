import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { useUser } from "@clerk/tanstack-react-start";
import { useBusiness } from "@/hooks/use-business";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { toast } from "sonner";

export const Route = createFileRoute("/profile")({
  head: () => ({ meta: [{ title: "Profile — Billix" }] }),
  component: ProfilePage,
});

function ProfilePage() {
  const { user, isLoaded } = useUser();
  const { activeBusiness } = useBusiness();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setFirstName(user.firstName || "");
      setLastName(user.lastName || "");
    }
  }, [user]);

  if (!isLoaded) {
    return (
      <AppShell>
        <PageHeader title="My Profile" description="Manage your personal details." />
        <div className="flex h-40 items-center justify-center text-sm text-muted-foreground animate-pulse">
          Loading profile details...
        </div>
      </AppShell>
    );
  }

  const primaryEmail = user?.primaryEmailAddress?.emailAddress || "N/A";
  const primaryPhone = user?.primaryPhoneNumber?.phoneNumber || "Not provided";
  const userInitials =
    user?.firstName && user?.lastName
      ? `${user.firstName[0]}${user.lastName[0]}`
      : primaryEmail.slice(0, 2).toUpperCase();

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setIsSaving(true);
    try {
      await user.update({
        firstName,
        lastName,
      });
      toast.success("Profile details updated successfully");
    } catch (err: unknown) {
      const error = err as Error;
      toast.error(error.message || "Failed to update profile details");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      <PageHeader title="My Profile" description="Manage your personal details and account info." />
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <CardContent className="flex flex-col items-center p-6 text-center">
            <Avatar className="h-24 w-24">
              <AvatarImage src={user?.imageUrl} alt={user?.fullName || "User Avatar"} />
              <AvatarFallback className="bg-primary text-2xl font-semibold text-primary-foreground">
                {userInitials}
              </AvatarFallback>
            </Avatar>
            <div className="mt-4 font-display text-lg font-semibold">
              {user?.fullName || `${firstName} ${lastName}`.trim() || primaryEmail}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {activeBusiness?.business_name
                ? `Owner · ${activeBusiness.business_name}`
                : "Authenticated User"}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Personal information</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveProfile} className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First name</Label>
                  <Input
                    id="firstName"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="First name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last name</Label>
                  <Input
                    id="lastName"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Last name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email address</Label>
                  <Input id="email" value={primaryEmail} disabled className="bg-muted/50" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Mobile number</Label>
                  <Input id="phone" value={primaryPhone} disabled className="bg-muted/50" />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Button type="submit" disabled={isSaving}>
                    {isSaving ? "Saving changes..." : "Save changes"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Account Security</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                Authentication and password management are secured via Clerk OAuth. You can manage
                your credentials and active sessions directly through your account security
                provider.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
