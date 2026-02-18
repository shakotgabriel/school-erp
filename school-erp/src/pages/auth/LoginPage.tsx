import { useMemo } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { paths } from "../../routes/paths";
import { useAuthStore } from "../../store/auth.store";
import { ApiError } from "../../lib/apiClient";

const schema = z.object({
	identifier: z.string().min(1, "Identifier is required"),
	password: z.string().min(1, "Password is required"),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
	const navigate = useNavigate();
	const location = useLocation();
	const login = useAuthStore((s) => s.login);
	const isLoading = useAuthStore((s) => s.isLoading);
	const error = useAuthStore((s) => s.error);
	const clearError = useAuthStore((s) => s.clearError);

	type LocationState = { from?: { pathname?: string } } | null | undefined;

	const fromPath = useMemo(() => {
		const state = location.state as LocationState;
		return typeof state?.from?.pathname === "string" ? state.from.pathname : paths.root;
	}, [location.state]);

	const form = useForm<FormValues>({
		resolver: zodResolver(schema),
		defaultValues: { identifier: "", password: "" },
	});

	function extractApiMessage(value: unknown): string | undefined {
		if (typeof value === "string") return value;
		if (Array.isArray(value) && value.length && typeof value[0] === "string") return value[0];
		return undefined;
	}

	return (
		<Card>
			<CardHeader>
				<CardTitle>Login</CardTitle>
				<CardDescription>Sign in with email or admission number.</CardDescription>
			</CardHeader>
			<CardContent>
				<form
					className="space-y-3 md:space-y-4"
					onSubmit={form.handleSubmit(async (values) => {
						clearError();
						try {
							await login(values);
							navigate(fromPath, { replace: true });
						} catch (err) {
						
							if (err instanceof ApiError && err.data && typeof err.data === "object") {
								const d = err.data as Record<string, unknown>;

							if (Array.isArray(d.non_field_errors) && d.non_field_errors.length) {
									form.setError("identifier", { type: "server", message: String(d.non_field_errors[0]) });
								} else if (d.detail && typeof d.detail === "string") {
									form.setError("identifier", { type: "server", message: d.detail });
								} else {
									
									if (d.identifier) {
										const v = extractApiMessage(d.identifier);
										if (v) form.setError("identifier", { type: "server", message: v });
									}
									if (d.password) {
										const v = extractApiMessage(d.password);
										if (v) form.setError("password", { type: "server", message: v });
									}
								}
							}
							
						}
					})}
				>
					<div className="space-y-1.5 md:space-y-2">
						<label className="text-sm font-medium">Identifier</label>
						<Input
							placeholder="Email or admission number"
							autoComplete="username"
							{...form.register("identifier")}
						/>
						{form.formState.errors.identifier?.message ? (
							<p className="text-xs md:text-sm text-destructive">{form.formState.errors.identifier.message}</p>
						) : null}
					</div>

					<div className="space-y-1.5 md:space-y-2">
						<label className="text-sm font-medium">Password</label>
						<Input
							type="password"
							placeholder="••••••••"
							autoComplete="current-password"
							{...form.register("password")}
						/>
						{form.formState.errors.password?.message ? (
							<p className="text-xs md:text-sm text-destructive">{form.formState.errors.password.message}</p>
						) : null}
					</div>

					{error ? <p className="text-xs md:text-sm text-destructive">{error}</p> : null}

					<Button type="submit" className="w-full" disabled={isLoading}>
						{isLoading ? "Signing in..." : "Sign in"}
					</Button>

					<div className="text-sm text-center">
						<Link className="underline" to={paths.forgotPassword}>
							Forgot password?
						</Link>
					</div>
				</form>
			</CardContent>
		</Card>
	);
}

