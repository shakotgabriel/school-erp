import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./sidebar/Sidebar";
import { useAuthStore } from "../store/auth.store";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";

export default function DashboardLayout() {
  const user = useAuthStore((s) => s.user);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Main */}
        <div className="flex-1">
          {/* Topbar */}
          <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-3">
                {/* Mobile menu button */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="md:hidden"
                  onClick={() => setSidebarOpen(true)}
                >
                  <Menu className="h-5 w-5" />
                </Button>
                <h1 className="text-base md:text-lg font-semibold">School ERP</h1>
                <span className="text-xs md:text-sm text-muted-foreground hidden sm:inline">
                  {user ? `${user.role.toUpperCase()} Portal` : ""}
                </span>
              </div>

              <div className="flex items-center gap-2 md:gap-3">
                <div className="hidden md:flex flex-col items-end leading-tight">
                  <span className="text-sm font-medium">
                    {user?.fullName ?? user?.email ?? "User"}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {user?.email ?? ""}
                  </span>
                </div>

                <Button variant="outline" size="sm" className="text-xs md:text-sm">
                  Profile
                </Button>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="p-3 md:p-4 lg:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
