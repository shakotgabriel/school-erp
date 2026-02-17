export type Role = "admin" | "teacher" | "accountant" | "hr" | "student";

export type AuthUser = {
	id: string;
	email: string;
	fullName?: string;
	role: Role;
};

