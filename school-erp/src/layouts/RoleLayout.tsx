import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthStore } from "../store/auth.store";
import { paths } from "../routes/paths";

function roleToPath(role: string) {
	switch (role) {
		case "admin":
			return paths.admin;
		case "teacher":
			return paths.teacher;
		case "accountant":
			return paths.accountant;
		case "hr":
			return paths.hr;
		case "student":
			return paths.student;
		default:
			return paths.root;
	}
}

export function RoleLayout() {
	const location = useLocation();
	const user = useAuthStore((s) => s.user);

	if (!user) return <Navigate to={paths.login} replace />;

	if (location.pathname === paths.root) {
		return <Navigate to={roleToPath(user.role)} replace />;
	}

	return <Outlet />;
}

