import Link from "next/link";
import { Button } from "~/components/ui/button"
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	CardDescription,
} from "~/components/ui/card";
import { ChannelBadgeNoLabel } from "~/components/ChannelBadge";
import type { ProcessedItemType } from "~/server/db/schema";

import styles from "./styles.module.css";
import { ROUTES } from "~/lib/nav_items";
import { api } from "~/trpc/server";
import { formatDistanceToNow } from "date-fns";

function getPriorityIcon(priority: 3 | 2 | 1): string {
	switch (priority) {
		case 3: return '🔴';
		case 2: return '🟠';
		case 1: return '🟡';
		default: return '⚪';
	}
}


export async function UrgentActionables() {
	const latest_items = await api.processed_items.getLatestAvailable({
		limit: 20,
		actionable: true,
		channel: 'all',
	});

	const priorities = {
		low: 0,
		medium: 0,
		high: 0,
		new: 0
	}

	latest_items.forEach(item => {
		if (item.urgency === 1) {
			priorities.low++;
		}
		else if (item.urgency === 2) {
			priorities.medium++;
		}
		else if (item.urgency === 3) {
			priorities.high++;
		}

		priorities.new++;
	});

	const latest_item = latest_items.length > 0 ? latest_items[0] : null;

	const highPriorityItems = latest_items.filter(item => item.urgency === 3);
	const mediumPriorityItems = latest_items.filter(item => item.urgency === 2);

	// Get channel counts
	const channelCounts = latest_items.reduce((acc, item) => {
		acc[item.type] = (acc[item.type] ?? 0) + 1;
		return acc;
	}, {} as Record<ProcessedItemType, number>);

	// Get top 3 items to display
	const topItems = [
		...highPriorityItems.slice(0, 3),
		...mediumPriorityItems.slice(0, Math.max(0, 3 - highPriorityItems.length))
	].slice(0, 3);

	return (
		<Card className="w-full">
			<CardHeader>
				<div className="flex items-center justify-between">
					<CardTitle className={styles.card_title}>
						Business Intelligence
					</CardTitle>
					<span className="text-[10px] uppercase tracking-wide">
						{latest_item ? 'Updated ' + formatDistanceToNow(latest_item.created_at, { addSuffix: true }) : 'No items found'}
					</span>
				</div>
				{/* <CardDescription>
					Urgent: <strong className="text-zinc-950 font-medium">{highCount} items</strong> ({totalActionable} total: {mediumCount} medium - {lowCount} low)
				</CardDescription> */}
				<CardDescription>
					<div className="flex items-center gap-4 mt-1">
						<div className="flex items-center gap-1.5">
							<div className={`${styles.some_rounded_thing} bg-red-100 text-red-700`}>
								{priorities.high}
							</div>
							<div className={`${styles.some_rounded_thing} bg-yellow-100 text-yellow-700`}>
								{priorities.medium}
							</div>
							<div className={`${styles.some_rounded_thing} bg-green-100 text-green-700`}>
								{priorities.low}
							</div>
							{/* <div className={`${styles.some_rounded_thing} bg-red-100 text-red-800`}>
								<Circle className="text-red-500" />2
								</div>
								<div className={`${styles.some_rounded_thing} bg-yellow-100 text-yellow-800`}>
								<Circle className="text-yellow-500" />3
								</div>
								<div className={`${styles.some_rounded_thing} bg-green-100 text-green-800`}>
								<Circle className="text-green-500" />4
							</div> */}
						</div>
						<div>New items: <strong className="text-zinc-950 font-medium">{priorities.new}</strong></div>
					</div>
				</CardDescription>

			</CardHeader>
			<CardContent className="flex flex-col pr-4 gap-2">
				<div className="flex flex-col gap-2 font-medium">Urgent items</div>
				{/* Top urgent items */}
				<div className="flex flex-col gap-2">
					{topItems.map((item, index) => (
						<Link href={`/items/${item.id}?ref=business-intelligence`} key={index} className="flex items-center gap-2 text-sm p-2 rounded-md bg-zinc-100 hover:bg-[#EEEFF0] transition-background">
							{/* <span>{getPriorityIcon(item.priority)}</span> */}
							<span className="size-6 text-gray-600"><ChannelBadgeNoLabel type={item.type} className="text-xs" /></span>
							<span className="font-medium">{item.client_name}</span>
							<span className="text-gray-600">–</span>
							<span className="text-gray-700">{item.data.short_description}</span>
						</Link>
					))}
				</div>

				{/* Channel badges */}
				<div className="flex items-center gap-4 flex-wrap mt-2">
					{Object.entries(channelCounts).map(([channel, count]) => (
						<div key={channel} className="flex items-center">
							<ChannelBadgeNoLabel type={channel as ProcessedItemType} className="text-xs" />
							<span className="text-sm font-medium">{count}</span>
						</div>
					))}
				</div>

				<Button className="w-full mt-2" variant="outline" asChild>
					<Link href={ROUTES.BUSINESS_INTELLIGENCE}>
						View all
					</Link>
				</Button>
			</CardContent>
		</Card>
	);
}

function Circle({ size = 8, className }: { size?: number, className?: string }) {
	return (
		<div className={className}>
			<svg width={size} height={size} fill="currentColor" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
				<circle cx="50" cy="50" r="50" />
			</svg>
		</div>
	);
}
