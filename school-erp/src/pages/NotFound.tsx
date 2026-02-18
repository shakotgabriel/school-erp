import { Link } from "react-router-dom";

import { Button } from "../components/ui/button";
import { paths } from "../routes/paths";

export default function NotFound() {
	return (
		<div className="min-h-screen flex items-center justify-center p-4 md:p-6">
			<div className="space-y-3 md:space-y-4 text-center">
				<div className="text-xl md:text-2xl font-semibold">Page not found</div>
				<Button asChild>
					<Link to={paths.root}>Go home</Link>
				</Button>
			</div>
		</div>
	);
}

