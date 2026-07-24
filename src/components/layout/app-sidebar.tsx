import { Link, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Building2,
  Users,
  Truck,
  Package,
  Tags,
  Boxes,
  FilePlus2,
  ReceiptText,
  BarChart3,
  LineChart,
  Settings,
  UserCircle2,
  Sparkles,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const sections = [
  {
    label: "Overview",
    items: [
      { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
      { title: "Analytics", url: "/analytics", icon: LineChart },
      { title: "Reports", url: "/reports", icon: BarChart3 },
    ],
  },
  {
    label: "Sales",
    items: [
      { title: "Create Invoice", url: "/invoices/new", icon: FilePlus2 },
      { title: "Invoice History", url: "/invoices", icon: ReceiptText },
      { title: "Customers", url: "/customers", icon: Users },
    ],
  },
  {
    label: "Inventory",
    items: [
      { title: "Products", url: "/products", icon: Package },
      { title: "Categories", url: "/categories", icon: Tags },
      { title: "Stock", url: "/inventory", icon: Boxes },
      { title: "Suppliers", url: "/suppliers", icon: Truck },
    ],
  },
  {
    label: "Account",
    items: [
      { title: "Business Profiles", url: "/business-profiles", icon: Building2 },
      { title: "Settings", url: "/settings", icon: Settings },
      { title: "User Profile", url: "/profile", icon: UserCircle2 },
    ],
  },
];

export function AppSidebar() {
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const isActive = (url: string) =>
    url === "/dashboard" ? pathname === url : pathname === url || pathname.startsWith(url + "/");

  return (
    <Sidebar collapsible="icon" className="border-r">
      <SidebarHeader className="border-b">
        <Link to="/dashboard" className="flex items-center gap-2 px-2 py-2">
          <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary text-primary-foreground shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="min-w-0 leading-tight group-data-[collapsible=icon]:hidden">
            <div className="truncate font-display text-base font-bold tracking-tight">Billix</div>
            <div className="truncate text-[11px] text-muted-foreground">
              GST · Billing · Inventory
            </div>
          </div>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        {sections.map((section) => (
          <SidebarGroup key={section.label}>
            <SidebarGroupLabel>{section.label}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {section.items.map((item) => (
                  <SidebarMenuItem key={item.url}>
                    <SidebarMenuButton asChild isActive={isActive(item.url)} tooltip={item.title}>
                      <Link to={item.url} className="flex items-center gap-2">
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarFooter className="border-t">
        <div className="rounded-lg bg-gradient-to-br from-primary/10 to-accent/40 p-3 text-xs group-data-[collapsible=icon]:hidden">
          <div className="font-semibold">Upgrade to Pro</div>
          <div className="mt-1 text-muted-foreground">
            Unlimited invoices, e-way bills and multi-branch.
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
