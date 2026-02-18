
import React, { useEffect } from "react";
import { Menu, Bell } from "lucide-react";
import { Button } from "../components/ui/button";
import { useAuthStore } from "../store/auth.store";

import { useNotificationStore } from "../store/notification.store";

interface HeaderProps {
	setSidebarOpen?: (open: boolean) => void;
}


export const Header: React.FC<HeaderProps> = ({ setSidebarOpen }) => {
	const user = useAuthStore((s) => s.user);
	const { notifications, fetchAll } = useNotificationStore();
	useEffect(() => {
		fetchAll();
		// Optionally, add polling or websocket for real-time updates
	}, [fetchAll]);
	const unreadCount = notifications.filter((n) => !n.read).length;
	return (
		<header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
			<div className="flex items-center gap-3 px-4 py-3">
				
				<div className="flex items-center gap-3">
					{setSidebarOpen && (
						<Button
							variant="ghost"
							size="sm"
							className="md:hidden"
							onClick={() => setSidebarOpen(true)}
						>
							<Menu className="h-5 w-5" />
						</Button>
					)}
					<h1 className="text-base md:text-lg font-semibold whitespace-nowrap">
						School ERP
					</h1>
				</div>

				<div className="flex-1 max-w-xl">
					<div className="relative">
						<input
							type="text"
							placeholder="Search students, classes, invoices..."
							className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
						/>
					</div>
				</div>

			
				<div className="flex items-center gap-3 ml-auto">
				
					<Button variant="ghost" size="icon" className="relative">
						<Bell className="h-5 w-5" />
						<span className="sr-only">Notifications</span>
						{unreadCount > 0 && (
							<span className="absolute -top-1 -right-1 h-4 min-w-4 rounded-full bg-red-500 px-1 text-[10px] leading-4 text-white text-center">
								{unreadCount}
							</span>
						)}
					</Button>

					<div className="hidden sm:flex flex-col items-end leading-tight">
						<span className="text-sm font-medium">
							{user?.fullName ?? user?.email ?? "User"}
						</span>
						<span className="text-xs text-muted-foreground">
							{user?.role ? user.role.toUpperCase() : ""}
						</span>
					</div>

					
					<div className="h-9 w-9 rounded-full border flex items-center justify-center text-sm font-semibold">
						{(user?.fullName?.[0] ?? user?.email?.[0] ?? "U").toUpperCase()}
					</div>
				</div>
			</div>
		</header>
	);
};

export default Header;
