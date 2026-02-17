import { useMemo, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { navByRole, type NavItem } from "./nav.config";
import { useAuthStore } from "../../store/auth.store";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronDown, LogOut } from "lucide-react";

function isPathActive(pathname: string, to?: string) {
  if (!to) return false;

  return pathname === to || pathname.startsWith(to + "/");
}

function NavGroup({
  item,
  pathname,
}: {
  item: NavItem;
  pathname: string;
}) {
  const hasChildren = !!item.children?.length;

  const initiallyOpen = useMemo(() => {
    if (!hasChildren) return false;
    return item.children!.some((c) => isPathActive(pathname, c.to));
  }, [hasChildren, item.children, pathname]);

  const [open, setOpen] = useState(initiallyOpen);

  if (!hasChildren) {
    const Icon = item.icon;
    return (
      <NavLink
        to={item.to!}
        className={({ isActive }) =>
          [
            "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
            "hover:bg-accent hover:text-accent-foreground",
            isActive ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground",
          ].join(" ")
        }
        end
      >
        {Icon ? <Icon className="h-4 w-4" /> : null}
        <span>{item.label}</span>
      </NavLink>
    );
  }

  const Icon = item.icon;

  return (
    <div className="space-y-1">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={[
          "w-full flex items-center justify-between rounded-md px-3 py-2 text-sm",
          "hover:bg-accent hover:text-accent-foreground",
          item.children!.some((c) => isPathActive(pathname, c.to))
            ? "text-foreground font-medium"
            : "text-muted-foreground",
        ].join(" ")}
      >
        <span className="flex items-center gap-2">
          {Icon ? <Icon className="h-4 w-4" /> : null}
          {item.label}
        </span>
        <ChevronDown className={`h-4 w-4 transition ${open ? "rotate-180" : ""}`} />
      </button>

      {open ? (
        <div className="ml-4 space-y-1">
          {item.children!.map((child) => {
            const ChildIcon = child.icon;
            return (
              <NavLink
                key={child.label}
                to={child.to!}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
                    "hover:bg-accent hover:text-accent-foreground",
                    isActive ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground",
                  ].join(" ")
                }
                end
              >
                {ChildIcon ? <ChildIcon className="h-4 w-4" /> : null}
                <span>{child.label}</span>
              </NavLink>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

export default function Sidebar() {
  const location = useLocation();
  const pathname = location.pathname;

  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const role = user?.role ?? "student";
  const items = navByRole[role] ?? [];

  return (
    <aside className="sticky top-0 h-screen w-64 border-r bg-background hidden md:flex flex-col">
      {/* Brand */}
      <div className="px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-base font-semibold">School ERP</div>
            <div className="text-xs text-muted-foreground">
              {role.toUpperCase()} Portal
            </div>
          </div>
        </div>
      </div>

      <Separator />

      
      <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        {items.map((item) => (
          <NavGroup key={item.label} item={item} pathname={pathname} />
        ))}
      </nav>

      <Separator />

    
      <div className="p-3 space-y-2">
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 text-muted-foreground"
          onClick={() => logout()}
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </aside>
  );
}
