import {
  LayoutDashboard,
  Users,
  ClipboardCheck,
  FileSpreadsheet,
  Calendar,
  Wallet,
  Receipt,
  BadgeCheck,
  Settings,
  Building2,
  GraduationCap,
  BookOpen,
  UserCog,
} from "lucide-react";
import type { ComponentType, SVGProps } from "react";

export type NavItem = {
  label: string;
  to?: string;
  icon?: ComponentType<SVGProps<SVGSVGElement>>;
  children?: NavItem[];
};

export const navByRole: Record<string, NavItem[]> = {
  admin: [
    { label: "Dashboard", to: "/admin/dashboard", icon: LayoutDashboard },
    { label: "Students", to: "/admin/students", icon: Users },
    { label: "Attendance", to: "/admin/attendance", icon: ClipboardCheck },
    { label: "Exams & Results", to: "/admin/exams", icon: FileSpreadsheet },
    { label: "Timetable", to: "/admin/timetable", icon: Calendar },
    {
      label: "Finance",
      icon: Wallet,
      children: [
        { label: "Fee Structures", to: "/admin/finance/fees", icon: BadgeCheck },
        { label: "Invoices", to: "/admin/finance/invoices", icon: Receipt },
        { label: "Payments", to: "/admin/finance/payments", icon: Wallet },
      ],
    },
    {
      label: "HR",
      icon: Building2,
      children: [
        { label: "Staff", to: "/admin/hr/staff", icon: GraduationCap },
        { label: "Payroll", to: "/admin/hr/payroll", icon: Wallet },
        { label: "Leave", to: "/admin/hr/leave", icon: BookOpen },
      ],
    },
    {
      label: "Settings",
      icon: Settings,
      children: [
        { label: "Academic Setup", to: "/admin/settings/academics", icon: BookOpen },
        { label: "Users & Roles", to: "/admin/settings/users", icon: UserCog },
      ],
    },
  ],

  teacher: [
    { label: "Dashboard", to: "/teacher/dashboard", icon: LayoutDashboard },
    { label: "Attendance", to: "/teacher/attendance", icon: ClipboardCheck },
    { label: "Results", to: "/teacher/results", icon: FileSpreadsheet },
    { label: "Timetable", to: "/teacher/timetable", icon: Calendar },
    { label: "Students", to: "/teacher/students", icon: Users }, // read-only
  ],

  accountant: [
    { label: "Dashboard", to: "/accountant/dashboard", icon: LayoutDashboard },
    { label: "Fee Structures", to: "/accountant/fees", icon: BadgeCheck },
    { label: "Invoices", to: "/accountant/invoices", icon: Receipt },
    { label: "Payments", to: "/accountant/payments", icon: Wallet },
    { label: "Receipts", to: "/accountant/receipts", icon: Receipt },
    { label: "Reports", to: "/accountant/reports", icon: FileSpreadsheet },
  ],

  hr: [
    { label: "Dashboard", to: "/hr/dashboard", icon: LayoutDashboard },
    { label: "Staff", to: "/hr/staff", icon: Users },
    { label: "Departments", to: "/hr/departments", icon: Building2 },
    { label: "Leave", to: "/hr/leave", icon: ClipboardCheck },
    { label: "Payroll", to: "/hr/payroll", icon: Wallet },
    { label: "Reports", to: "/hr/reports", icon: FileSpreadsheet },
  ],

  student: [
    { label: "Dashboard", to: "/student/dashboard", icon: LayoutDashboard },
    { label: "My Results", to: "/student/results", icon: FileSpreadsheet },
    { label: "My Fees", to: "/student/fees", icon: Wallet },
    { label: "My Timetable", to: "/student/timetable", icon: Calendar },
  ],
};
