import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AuthLayout } from "./layouts/AuthLayout";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { RoleLayout } from "./layouts/RoleLayout";
import AdminDashboard from "./pages/AdminDashboard";
import AccountantDashboard from "./pages/AccountantDashboard";
import HRDashboard from "./pages/HRDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import NotFound from "./pages/NotFound";
import ForgotPasswordPage from "./pages/auth/ForgotPasswordPage";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/registerpage";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { paths } from "./routes/paths";
import { RoleRoute } from "./routes/RoleRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AuthLayout />}>
          <Route path={paths.login} element={<LoginPage />} />
          <Route path={paths.forgotPassword} element={<ForgotPasswordPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<RoleLayout />}>
            <Route element={<DashboardLayout />}>
              <Route path={paths.root} element={<div />} />

              <Route element={<RoleRoute allowedRoles={["admin"]} />}>
                <Route path={paths.admin} element={<AdminDashboard />} />
                <Route path={paths.adminRegister} element={<RegisterPage />} />
              </Route>

              <Route element={<RoleRoute allowedRoles={["teacher"]} />}>
                <Route path={paths.teacher} element={<TeacherDashboard />} />
              </Route>

              <Route element={<RoleRoute allowedRoles={["accountant"]} />}>
                <Route path={paths.accountant} element={<AccountantDashboard />} />
              </Route>

              <Route element={<RoleRoute allowedRoles={["hr"]} />}>
                <Route path={paths.hr} element={<HRDashboard />} />
              </Route>

              <Route element={<RoleRoute allowedRoles={["student"]} />}>
                <Route path={paths.student} element={<StudentDashboard />} />
              </Route>
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
