import { useMemo, useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { navByRole, type NavItem } from "./nav.config";
import { useAuthStore } from "../../store/auth.store";
import { Button } from "@/components/ui/button";
import { ChevronDown, LogOut, X } from "lucide-react";

function isPathActive(pathname: string, to?: string) {
  if (!to) return false;
  return pathname === to || pathname.startsWith(to + "/");
}

function NavGroup({ item, pathname }: { item: NavItem; pathname: string }) {
  const hasChildren = !!item.children?.length;

  const initiallyOpen = useMemo(() => {
    if (!hasChildren) return false;
    return item.children!.some((c) => isPathActive(pathname, c.to));
  }, [hasChildren, item.children, pathname]);

  const [open, setOpen] = useState(initiallyOpen);

  const baseLink =
    "group flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm transition";
  const inactive =
    "text-muted-foreground hover:bg-accent hover:text-accent-foreground";
  const active =
    "bg-accent text-accent-foreground font-medium shadow-sm";

  if (!hasChildren) {
    const Icon = item.icon;
    return (
      <NavLink
        to={item.to!}
        className={({ isActive }) =>
          [baseLink, isActive ? active : inactive].join(" ")
        }
        end
      >
        {Icon ? (
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-muted/60 group-hover:bg-muted">
            <Icon className="h-4 w-4" />
          </span>
        ) : null}
        <span className="truncate">{item.label}</span>
      </NavLink>
    );
  }

  const Icon = item.icon;
  const groupIsActive = item.children!.some((c) => isPathActive(pathname, c.to));

  return (
    <div className="space-y-1">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={[
          "w-full flex items-center justify-between rounded-xl px-3 py-2.5 text-sm transition",
          groupIsActive
            ? "text-foreground font-medium bg-muted/40"
            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
        ].join(" ")}
      >
        <span className="flex items-center gap-2">
          {Icon ? (
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-muted/60">
              <Icon className="h-4 w-4" />
            </span>
          ) : null}
          <span className="truncate">{item.label}</span>
        </span>

        <ChevronDown
          className={`h-4 w-4 transition ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open ? (
        <div className="ml-3 border-l pl-3 space-y-1">
          {item.children!.map((child) => {
            const ChildIcon = child.icon;
            return (
              <NavLink
                key={child.label}
                to={child.to!}
                className={({ isActive }) =>
                  [
                    "group flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition",
                    isActive ? active : inactive,
                  ].join(" ")
                }
                end
              >
                {ChildIcon ? <ChildIcon className="h-4 w-4" /> : null}
                <span className="truncate">{child.label}</span>
              </NavLink>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

export default function Sidebar({
  open,
  onClose,
}: {
  open?: boolean;
  onClose?: () => void;
}) {
  const { pathname } = useLocation();

  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const role = user?.role ?? "student";
  const items = navByRole[role] ?? [];

  useEffect(() => {
    if (onClose) onClose();
  }, [onClose, pathname]);

 

  return (
    <>
      
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[2px] md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={[
          "fixed md:sticky top-0 z-50 h-screen w-72 border-r bg-background",
          "flex flex-col transition-transform duration-300 md:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        ].join(" ")}
      >
        
        <div className="relative px-4 pt-4 pb-3 bg-cyan-900">
         
          <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-muted/60 to-transparent" />

          <div className="relative flex items-start justify-between gap-3 ">
            <div className="flex items-center gap-3">
              <div className="h-30 w-30 overflow-hidden rounded-2xl border-white border-2 bg-muted/40 shadow-sm">
                <img
                  src="/EduPlan.png"
                  alt="School ERP"
                  className="h-full w-full "
                />
              </div>

              <div>
             
<div className="">
  <h1 className=" font-black text-white">SCHOOL ERP SYSTEM</h1>
</div>
            
              </div>
            </div>

            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={onClose}
              aria-label="Close sidebar"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

  

     
        <nav className="flex-1 overflow-y-auto px-3 py-3 bg-slate-800">
          <div className="mb-2 px-2 text-[11px] font-medium tracking-wide text-muted-foreground">
      
          </div>

          <div className="space-y-1  p-10 text-white">
            {items.map((item) => (
              <NavGroup  key={item.label} item={item} pathname={pathname} />
            ))}
          </div>
        </nav>

    

   
        <div className="p-4 ">


          <Button
            variant="outline"
            className="w-full justify-start gap-2 rounded-xl"
            onClick={logout}
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>
    </>
  );
}
