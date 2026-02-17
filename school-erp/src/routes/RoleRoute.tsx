import { Navigate, Outlet } from "react-router-dom";

import type { Role } from "../store/auth.store";
import { useAuthStore } from "../store/auth.store";
import { paths } from "./paths";

export function RoleRoute(props: { allowedRoles: Role[] }) {
	const role = useAuthStore((s) => s.user?.role);

	if (!role) return <Navigate to={paths.login} replace />;
	if (!props.allowedRoles.includes(role)) return <Navigate to={paths.root} replace />;

	return <Outlet />;
}

