import { useState } from "react";
import { Link } from "react-router-dom";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { requestPasswordResetApi } from "../../lib/auth";
import { paths } from "../../routes/paths";

const schema = z.object({
	email: z.string().email("Enter a valid email"),
});

type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
	const [isLoading, setIsLoading] = useState(false);
	const [message, setMessage] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const form = useForm<FormValues>({
		resolver: zodResolver(schema),
		defaultValues: { email: "" },
	});

	return (
		<Card>
			<CardHeader>
				<CardTitle>Reset password</CardTitle>
				<CardDescription>We’ll send reset instructions to your email.</CardDescription>
			</CardHeader>
			<CardContent>
				<form
					className="space-y-3 md:space-y-4"
					onSubmit={form.handleSubmit(async (values) => {
						setIsLoading(true);
						setError(null);
						setMessage(null);
						try {
							const res = await requestPasswordResetApi({ email: values.email });
							setMessage(res.debug_token ? `${res.message} (debug token: ${res.debug_token})` : res.message);
						} catch (e) {
							setError(e instanceof Error ? e.message : "Request failed");
						} finally {
							setIsLoading(false);
						}
					})}
				>
					<div className="space-y-1.5 md:space-y-2">
						<label className="text-sm font-medium">Email</label>
						<Input placeholder="name@school.com" autoComplete="email" {...form.register("email")} />
						{form.formState.errors.email?.message ? (
							<p className="text-xs md:text-sm text-destructive">{form.formState.errors.email.message}</p>
						) : null}
					</div>

					{message ? <p className="text-xs md:text-sm text-muted-foreground">{message}</p> : null}
					{error ? <p className="text-xs md:text-sm text-destructive">{error}</p> : null}

					<Button type="submit" className="w-full" disabled={isLoading}>
						{isLoading ? "Sending..." : "Send reset link"}
					</Button>

					<div className="text-sm text-center">
						<Link className="underline" to={paths.login}>
							Back to login
						</Link>
					</div>
				</form>
			</CardContent>
		</Card>
	);
}

