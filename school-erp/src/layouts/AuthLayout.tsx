import { Outlet } from "react-router-dom";

export function AuthLayout() {
	return (
		<div className="min-h-screen flex items-center justify-center p-4 md:p-6 bg-background">
			<div className="w-full max-w-md">
				<Outlet />
			</div>
		</div>
	);
}

