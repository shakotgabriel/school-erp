import { Outlet, useNavigate } from "react-router-dom";

import { Button } from "../components/ui/button";
import { useAuthStore } from "../store/auth.store";
import { paths } from "../routes/paths";

export function DashboardLayout() {
	const navigate = useNavigate();
	const logout = useAuthStore((s) => s.logout);
	const user = useAuthStore((s) => s.user);

	return (
		<div className="min-h-screen">
			<header className="flex items-center justify-between border-b px-6 py-4">
				<div className="text-sm">
					<div className="font-medium">School ERP</div>
					<div className="text-muted-foreground">{user?.email} · {user?.role}</div>
				</div>
				<Button
					variant="outline"
					onClick={() => {
						logout();
						navigate(paths.login, { replace: true });
					}}
				>
					Logout
				</Button>
			</header>

			<main className="p-6">
				<Outlet />
			</main>
		</div>
	);
}

