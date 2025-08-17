import { SidebarProvider } from "~/components/ui/sidebar";
import { AppSidebar } from "~/components/sidebar/app-sidebar";

export default function DashboardLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<SidebarProvider>
			<AppSidebar />
			{children}
		</SidebarProvider>
	);
}
