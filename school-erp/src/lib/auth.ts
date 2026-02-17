import { api, toApiError } from "./apiClient";
import type { AuthUser, Role } from "../types/user";

type BackendUser = {
	id: string | number;
	email: string;
	full_name?: string;
	role: Role;
	first_name?: string;
	last_name?: string;
};

export type LoginResponse = {
	tokens: {
		access: string;
		refresh: string;
	};
	user: BackendUser;
};

function mapUser(user: BackendUser): AuthUser {
	return {
		id: String(user.id),
		email: user.email,
		fullName: user.full_name,
		role: user.role,
	};
}

export async function loginApi(payload: { identifier: string; password: string }) {
	try {
		const { data } = await api.post<LoginResponse>("/users/login/", payload);
		return {
			accessToken: data.tokens.access,
			refreshToken: data.tokens.refresh,
			user: mapUser(data.user),
		};
	} catch (e) {
		throw toApiError(e);
	}
}

export async function meApi() {
	try {
		const { data } = await api.get<BackendUser>("/users/me/");
		return mapUser(data);
	} catch (e) {
		throw toApiError(e);
	}
}

export async function requestPasswordResetApi(payload: { email: string }) {
	try {
		const { data } = await api.post<{ message: string; debug_token?: string }>(
			"/users/password-reset/request/",
			payload
		);
		return data;
	} catch (e) {
		throw toApiError(e);
	}
}

export async function confirmPasswordResetApi(payload: { token: string; newPassword: string }) {
	try {
		const { data } = await api.post<{ message: string }>("/users/password-reset/confirm/", {
			token: payload.token,
			new_password: payload.newPassword,
		});
		return data;
	} catch (e) {
		throw toApiError(e);
	}
}

export async function registerApi(payload: {
	fullName: string;
	email?: string;
	role: Role;
	password: string;
	admissionNumber?: string;
	phoneNumber?: string;
}) {
	try {
		const names = payload.fullName?.trim().split(" ") || [];
		const first_name = names.shift() || "";
		const last_name = names.join(" ") || "";

		const body: Record<string, unknown> = {
			first_name,
			last_name,
			role: payload.role,
			password: payload.password,
		};

		if (payload.email) body.email = payload.email;
		if (payload.admissionNumber) body.admission_number = payload.admissionNumber;
		if (payload.phoneNumber) body.phone_number = payload.phoneNumber;

		const { data } = await api.post<{ message: string; user?: unknown }>("/users/register/", body);
		return data;
	} catch (e) {
		throw toApiError(e);
	}
}

