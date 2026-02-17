import axios, { AxiosError } from "axios";

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000/api";
const baseURL = rawBaseUrl.replace(/\/+$/, "");

export const api = axios.create({
	baseURL,
	headers: {
		Accept: "application/json",
	},
});

export function setApiAccessToken(accessToken: string | null) {
	if (accessToken) {
		api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
	} else {
		delete api.defaults.headers.common.Authorization;
	}
}

export type ApiErrorPayload = unknown;

export class ApiError extends Error {
	status: number | null;
	data: ApiErrorPayload;

	constructor(message: string, status: number | null, data: ApiErrorPayload) {
		super(message);
		this.name = "ApiError";
		this.status = status;
		this.data = data;
	}
}

export function toApiError(error: unknown): ApiError {
	if (error instanceof ApiError) return error;

	if (axios.isAxiosError(error)) {
		const axiosError = error as AxiosError;
		const status = axiosError.response?.status ?? null;
		const data = axiosError.response?.data;

	let message: string | undefined;
		if (typeof data === "object" && data !== null) {
			if ("detail" in data && typeof (data as any).detail === "string") {
				message = (data as any).detail;
			} else if ("message" in data && typeof (data as any).message === "string") {
				message = (data as any).message;
			} else {
				
				for (const key of Object.keys(data)) {
					const val = (data as any)[key];
					if (Array.isArray(val) && val.length && typeof val[0] === "string") {
						message = val[0];
						break;
					}
					if (typeof val === "string") {
						message = val;
						break;
					}
				}
			}
		}

		if (!message) message = axiosError.message || "Request failed";

		return new ApiError(message, status, data);
	}

	const message = error instanceof Error ? error.message : "Request failed";
	return new ApiError(message, null, null);
}

