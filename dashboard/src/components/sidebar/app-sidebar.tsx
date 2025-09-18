"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupContent,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarHeader,
	SidebarMenu,
  } from "~/components/ui/sidebar"

import { Logo } from "~/components/digital_excellence_logo"
import { ROUTES } from "~/lib/nav_items"
import { Home, Newspaper, TrendingUp } from "lucide-react"
import { NavUser } from "~/components/sidebar/nav-user"


// Menu items.
const items = [
	{
		title: "Home",
		url: ROUTES.HOME,
		icon: Home,
	},
	{
		title: "Latest Items",
		url: ROUTES.LATEST_ITEMS,
		icon: Newspaper,
	},
	{
		title: "Business Intelligence",
		url: ROUTES.BUSINESS_INTELLIGENCE,
		icon: TrendingUp,
	}
];

export function AppSidebar({ refParam }: { refParam?: string })
{
	const ref = refParam ?? ''
	const pathname = usePathname()

	const isActive = (itemUrl: string) => {
		// If we have a ref, prefer it
		if ('/' + ref === ROUTES.BUSINESS_INTELLIGENCE && itemUrl === ROUTES.BUSINESS_INTELLIGENCE) {
			return true
		}
		if ('/' + ref === ROUTES.LATEST_ITEMS && itemUrl === ROUTES.LATEST_ITEMS) {
			return true
		}

		if (itemUrl === ROUTES.HOME) {
			return pathname === itemUrl
		}

		return pathname.startsWith(itemUrl)
	}


	return (
		<Sidebar className="!border-0">
			<SidebarHeader className="pl-3">
				<Link href={ROUTES.HOME} className="py-4">
					<Logo />
				</Link>
				</SidebarHeader>
				<SidebarContent>
					<SidebarGroup>
						<SidebarGroupContent>
							<SidebarMenu>
							{items.map((item) => (
								<SidebarMenuItem key={item.title}>
									<SidebarMenuButton
										asChild
										isActive={isActive(item.url)}
										size="default"
										className="rounded-full h-10 pl-5 text-[15px] [&>svg]:size-4 data-[active=true]:bg-[#d3efff]"
									>
										<Link href={item.url}>
											<item.icon />
											<span>{item.title}</span>
										</Link>
									</SidebarMenuButton>
								</SidebarMenuItem>
							))}
							</SidebarMenu>
						</SidebarGroupContent>
					</SidebarGroup>
				</SidebarContent>
			<SidebarFooter>
				<NavUser />
			</SidebarFooter>
		</Sidebar>
	)
}