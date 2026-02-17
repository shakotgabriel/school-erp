import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/auth.store";

type Role = "admin" | "teacher" | "accountant" | "hr" | "student";

export function RoleRoute({ allowedRoles }: { allowedRoles: Role[] }) {
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.accessToken);

 
  if (!token || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }


  if (!allowedRoles.includes(user.role)) {
    
    const map: Record<Role, string> = {
      admin: "/admin/dashboard",
      teacher: "/teacher/dashboard",
      accountant: "/accountant/dashboard",
      hr: "/hr/dashboard",
      student: "/student/dashboard",
    };
    return <Navigate to={map[user.role]} replace />;
  }

  return <Outlet />;
}
