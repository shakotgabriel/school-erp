// src/layouts/dashboard/dashboard.config.ts

export type Role = "admin" | "teacher" | "accountant" | "hr" | "student";

export type MetricFormat = "number" | "currency" | "percent" | "text";

export type DashboardMetric = {
  key: string; // supports dot path: "finance.this_month.revenue"
  label: string;
  format?: MetricFormat;
  helperText?: string;
};

export type QuickAction = {
  label: string;
  to: string;
  variant?: "default" | "secondary" | "outline";
};

export type DashboardWidget =
  | { type: "overview_breakdown"; title: string }
  | { type: "finance_trends"; title: string }
  | { type: "finance_invoices"; title: string }
  | { type: "staff_today_attendance"; title: string }
  | { type: "leaves_pending"; title: string }
  | { type: "academic_structure"; title: string }
  | { type: "enrollment_by_class"; title: string }
  | { type: "timetables_summary"; title: string };

export type RoleDashboardConfig = {
  role: Role;
  title: string;
  defaultRoute: string;

  /**
   * These are your existing endpoints (relative to /api/dashboard/)
   * - overview -> GET /api/dashboard/overview/
   * - finance  -> GET /api/dashboard/finance/
   * - staff    -> GET /api/dashboard/staff/
   * - academic -> GET /api/dashboard/academic/
   */
  endpoints: Array<"overview" | "finance" | "staff" | "academic">;

  metrics: DashboardMetric[];
  quickActions: QuickAction[];
  widgets: DashboardWidget[];
};

export const dashboardByRole: Record<Role, RoleDashboardConfig> = {
  admin: {
    role: "admin",
    title: "Admin Dashboard",
    defaultRoute: "/admin/dashboard",
    endpoints: ["overview"],

    metrics: [
      { key: "overview.students.active_enrollments", label: "Active Enrollments", format: "number" },
      { key: "students.total_students", label: "Total Students", format: "number" },
      { key: "students.active_students", label: "Active Students", format: "number" },
      { key: "students.attendance.today.present", label: "Present Today", format: "number" },
      { key: "students.attendance.today.absent", label: "Absent Today", format: "number" },
      { key: "overview.finance.this_month.revenue", label: "Revenue (This Month)", format: "currency" },
      { key: "overview.finance.outstanding", label: "Outstanding Fees", format: "currency" },
    ],

    quickActions: [
      { label: "Add Student", to: "/admin/students/create", variant: "default" },
      { label: "Admission Applications", to: "/admin/admission/applications", variant: "secondary" },
      { label: "Mark Attendance", to: "/admin/attendance", variant: "secondary" },
      { label: "Record Payment", to: "/admin/finance/payments", variant: "outline" },
    ],

    widgets: [
      { type: "enrollment_by_class", title: "Enrollment by Class" },
      { type: "staff_today_attendance", title: "Staff Attendance Today" },
      { type: "leaves_pending", title: "Pending Leave Requests" },
    ],
  },

  accountant: {
    role: "accountant",
    title: "Finance Dashboard",
    defaultRoute: "/accountant/dashboard",
    endpoints: ["finance"],

    metrics: [
      { key: "revenue.total", label: "Total Revenue", format: "currency" },
      { key: "expenses.total", label: "Total Expenses", format: "currency" },
      { key: "invoices.outstanding", label: "Outstanding", format: "currency" },
      { key: "invoices.overdue", label: "Overdue Invoices", format: "number" },
      { key: "budgets.utilization_percentage", label: "Budget Utilization", format: "percent" },
    ],

    quickActions: [
      { label: "Record Payment", to: "/accountant/payments", variant: "default" },
      { label: "Create Invoice", to: "/accountant/invoices/create", variant: "secondary" },
      { label: "Add Expense", to: "/accountant/expenses/create", variant: "outline" },
      { label: "Reports", to: "/accountant/reports", variant: "outline" },
    ],

    widgets: [
      { type: "finance_invoices", title: "Invoices Summary" },
      { type: "finance_trends", title: "6-Month Trend" },
    ],
  },

  hr: {
    role: "hr",
    title: "HR Dashboard",
    defaultRoute: "/hr/dashboard",
    endpoints: ["staff"],

    metrics: [
      { key: "staff.total", label: "Total Staff", format: "number" },
      { key: "leaves.pending", label: "Pending Leaves", format: "number" },
      { key: "attendance.today.present", label: "Present Today", format: "number" },
      { key: "attendance.today.absent", label: "Absent Today", format: "number" },
      { key: "payroll.current_month_total", label: "Payroll (This Month)", format: "currency" },
    ],

    quickActions: [
      { label: "Add Staff", to: "/hr/staff/create", variant: "default" },
      { label: "Review Leave", to: "/hr/leave", variant: "secondary" },
      { label: "Mark Attendance", to: "/hr/attendance", variant: "secondary" },
      { label: "Payroll", to: "/hr/payroll", variant: "outline" },
    ],

    widgets: [
      { type: "leaves_pending", title: "Pending Leave Requests" },
      { type: "staff_today_attendance", title: "Attendance Today" },
    ],
  },

  teacher: {
    role: "teacher",
    title: "Teacher Dashboard",
    defaultRoute: "/teacher/dashboard",

    // You don't yet have /api/dashboard/teacher/ response.
    // For now use academic (structure + exams counts) until you add teacher endpoint.
    endpoints: ["academic"],

    metrics: [
      { key: "structure.classes", label: "Classes", format: "number" },
      { key: "teachers.total_assignments", label: "My Assignments", format: "number" },
      { key: "exams.upcoming", label: "Upcoming Exams", format: "number" },
      { key: "results.average_score", label: "Average Score", format: "percent" },
    ],

    quickActions: [
      { label: "Mark Attendance", to: "/teacher/attendance", variant: "default" },
      { label: "Enter Results", to: "/teacher/results", variant: "secondary" },
      { label: "My Timetable", to: "/teacher/timetable", variant: "outline" },
    ],

    widgets: [
      { type: "academic_structure", title: "Academic Summary" },
      { type: "timetables_summary", title: "Timetable Summary" },
    ],
  },

  student: {
    role: "student",
    title: "Student Dashboard",
    defaultRoute: "/student/dashboard",

    // You don’t have /api/dashboard/student/ yet.
    // For now, you can show read-only academic counts + later add student endpoint.
    endpoints: ["academic"],

    metrics: [
      { key: "exams.upcoming", label: "Upcoming Exams", format: "number" },
      { key: "results.average_score", label: "Average Score", format: "percent" },
      { key: "structure.subjects", label: "Subjects", format: "number" },
    ],

    quickActions: [
      { label: "My Results", to: "/student/results", variant: "default" },
      { label: "My Fees", to: "/student/fees", variant: "secondary" },
      { label: "My Timetable", to: "/student/timetable", variant: "outline" },
    ],

    widgets: [
      { type: "timetables_summary", title: "Timetable" },
      { type: "academic_structure", title: "Academics" },
    ],
  },
};

export function getDashboardConfig(role?: string | null): RoleDashboardConfig {
  const r = (role ?? "student") as Role;
  return dashboardByRole[r] ?? dashboardByRole.student;
}
