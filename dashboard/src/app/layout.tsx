import "~/styles/globals.css";

import { type Metadata } from "next";
import { Geist } from "next/font/google";
import { Suspense } from "react";

import { TRPCReactProvider } from "~/trpc/react";
import { SidebarProvider } from "~/components/ui/sidebar";
import { AppSidebar } from "~/components/sidebar/app-sidebar";

export const metadata: Metadata = {
	title: "AI APP",
	description: "AI APP",
	icons: [{ rel: "icon", url: "/favicon.ico" }],
};

const geist = Geist({
	subsets: ["latin"],
	variable: "--font-geist-sans",
});

export default function RootLayout({
	children,
}: Readonly<{ children: React.ReactNode }>)
{
	return (
		<html lang="en" className={`${geist.variable}`}>
			<body>
				<SidebarProvider>
					<Suspense fallback={null}>
						<AppSidebar />
					</Suspense>
					<TRPCReactProvider>
						{children}
					</TRPCReactProvider>
				</SidebarProvider>
			</body>
		</html>
	);
}
