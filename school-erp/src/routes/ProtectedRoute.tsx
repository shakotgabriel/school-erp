import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthStore } from "../store/auth.store";
import { paths } from "./paths";

export function ProtectedRoute() {
	const location = useLocation();
	const isAuthed = useAuthStore((s) => Boolean(s.accessToken && s.user));

	if (!isAuthed) {
		return <Navigate to={paths.login} replace state={{ from: location }} />;
	}

	return <Outlet />;
}

