import { Bell, Search, HelpCircle, Plus, Moon, Sun, Check } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { useUser, useAuth } from "@clerk/tanstack-react-start";
import { useBusiness } from "@/hooks/use-business";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

export function AppTopbar() {
  const [dark, setDark] = useState(false);
  const { user } = useUser();
  const { signOut } = useAuth();
  const { activeBusiness, activeBusinessId, businesses, switchBusiness } = useBusiness();

  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
  }, [dark]);

  const userInitials =
    user?.firstName && user?.lastName
      ? `${user.firstName[0]}${user.lastName[0]}`
      : user?.primaryEmailAddress?.emailAddress?.slice(0, 2).toUpperCase() || "US";

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur-md md:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="h-6" />

      <div className="relative hidden max-w-md flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Quick search invoices, customers, products… (⌘K)"
          className="h-9 rounded-lg border-muted bg-muted/40 pl-9 text-xs focus-visible:bg-background focus-visible:ring-1 transition-colors"
        />
        <kbd className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rounded border bg-background px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground shadow-2xs">
          ⌘K
        </kbd>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <Button asChild size="sm" className="hidden gap-1.5 font-medium shadow-sm sm:inline-flex">
          <Link to="/invoices/new">
            <Plus className="h-4 w-4" /> New Invoice
          </Link>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setDark((v) => !v)}
          aria-label="Toggle theme"
          className="h-9 w-9 text-muted-foreground hover:text-foreground"
        >
          {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="relative h-9 w-9 text-muted-foreground hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          <Badge className="absolute -right-0.5 -top-0.5 h-4 min-w-4 rounded-full p-0 px-1 text-[10px] bg-primary text-primary-foreground font-bold">
            3
          </Badge>
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2.5 rounded-full pl-1 pr-2.5 py-1 hover:bg-muted/70 outline-none transition-colors">
              <Avatar className="h-7 w-7 border shadow-2xs">
                <AvatarImage src={user?.imageUrl} alt={user?.fullName || "User Avatar"} />
                <AvatarFallback className="bg-primary text-primary-foreground text-xs font-semibold">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="hidden text-left leading-tight sm:block">
                <div className="text-xs font-bold text-foreground">
                  {user?.fullName ||
                    user?.primaryEmailAddress?.emailAddress ||
                    "Authenticated User"}
                </div>
                <div className="text-[10px] text-muted-foreground truncate max-w-[120px] font-medium">
                  {activeBusiness?.business_name || "No Active Business"}
                </div>
              </div>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-60 shadow-lg">
            <DropdownMenuLabel className="font-semibold">My Workspace Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link to="/profile">Profile Settings</Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/settings">System Preferences</Link>
            </DropdownMenuItem>

            {businesses.length > 0 && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuLabel className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Switch Active Business
                </DropdownMenuLabel>
                {businesses.map((b) => (
                  <DropdownMenuItem
                    key={b.id}
                    onClick={() => switchBusiness(b.id)}
                    className={`flex justify-between items-center text-xs py-2 ${
                      b.id === activeBusinessId ? "font-bold bg-primary/10 text-primary" : ""
                    }`}
                  >
                    <span className="truncate max-w-[170px]">{b.business_name}</span>
                    {b.id === activeBusinessId && <Check className="h-3.5 w-3.5 text-primary" />}
                  </DropdownMenuItem>
                ))}
              </>
            )}

            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => signOut()} className="text-destructive font-medium">
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
