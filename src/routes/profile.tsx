import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export const Route = createFileRoute("/profile")({
  head: () => ({ meta: [{ title: "Profile — Billix" }] }),
  component: ProfilePage,
});

function ProfilePage() {
  return (
    <AppShell>
      <PageHeader title="My Profile" description="Manage your personal details and password." />
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <CardContent className="flex flex-col items-center p-6 text-center">
            <Avatar className="h-24 w-24">
              <AvatarFallback className="bg-primary text-2xl text-primary-foreground">RS</AvatarFallback>
            </Avatar>
            <div className="mt-4 font-display text-lg font-semibold">Rahul Sharma</div>
            <div className="text-xs text-muted-foreground">Owner · Sharma Retail Store</div>
            <Button variant="outline" size="sm" className="mt-4">Change photo</Button>
          </CardContent>
        </Card>
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Personal information</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2"><Label>First name</Label><Input defaultValue="Rahul" /></div>
              <div className="space-y-2"><Label>Last name</Label><Input defaultValue="Sharma" /></div>
              <div className="space-y-2"><Label>Email</Label><Input defaultValue="rahul@sharmaretail.in" /></div>
              <div className="space-y-2"><Label>Mobile</Label><Input defaultValue="+91 98765 43210" /></div>
              <div className="space-y-2 sm:col-span-2"><Button>Save changes</Button></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Security</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2"><Label>Current password</Label><Input type="password" /></div>
              <div className="space-y-2"><Label>New password</Label><Input type="password" /></div>
              <div className="space-y-2 sm:col-span-2"><Button variant="outline">Update password</Button></div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}