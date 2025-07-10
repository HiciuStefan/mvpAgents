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

type UrgentActionableType = {
	company: string;
	reason: string;
	priority: 'high' | 'medium' | 'low';
	channel: ProcessedItemType | 'whatsapp';
	overdueDuration?: string;
}

const mock_data: UrgentActionableType[] = [
	{
		company: 'UI Path',
		reason: 'SLA overdue 36 h',
		priority: 'high',
		channel: 'email'
	},
	{
		company: 'Liverpool FC',
		reason: 'Prototype request (WhatsApp)',
		priority: 'high',
		channel: 'whatsapp'
	},
	{
		company: 'Acme Corp',
		reason: 'Contract renewal due',
		priority: 'medium',
		channel: 'email'
	},
	{
		company: 'Globex Inc',
		reason: 'Meeting follow-up',
		priority: 'medium',
		channel: 'website'
	},
	{
		company: 'Wayne Enterprises',
		reason: 'Budget approval needed',
		priority: 'medium',
		channel: 'email'
	},
	{
		company: 'Stark Industries',
		reason: 'Technical review',
		priority: 'low',
		channel: 'twitter'
	},
	{
		company: 'LexCorp',
		reason: 'Quarterly check-in',
		priority: 'low',
		channel: 'email'
	},
	{
		company: 'Oscorp',
		reason: 'Documentation update',
		priority: 'low',
		channel: 'website'
	},
	{
		company: 'InGen',
		reason: 'Status report',
		priority: 'low',
		channel: 'twitter'
	}
];

export async function fetchMockData(): Promise<UrgentActionableType[]> {
	return new Promise((resolve) => {
		resolve(mock_data);
	});
}

function getPriorityIcon(priority: 'high' | 'medium' | 'low'): string {
	switch (priority) {
		case 'high': return '🔴';
		case 'medium': return '🟠';
		case 'low': return '🟡';
		default: return '⚪';
	}
}

export async function UrgentActionables() {
	const data = await fetchMockData();

	const highPriorityItems = data.filter(item => item.priority === 'high');
	const mediumPriorityItems = data.filter(item => item.priority === 'medium');
	const lowPriorityItems = data.filter(item => item.priority === 'low');

	const totalActionable = data.length;
	const highCount = highPriorityItems.length;
	const mediumCount = mediumPriorityItems.length;
	const lowCount = lowPriorityItems.length;

	// Get channel counts
	const channelCounts = data.reduce((acc, item) => {
		acc[item.channel] = (acc[item.channel] ?? 0) + 1;
		return acc;
	}, {} as Record<ProcessedItemType | 'whatsapp', number>);

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
						Updated 2 min ago
					</span>
				</div>
				{/* <CardDescription>
					Urgent: <strong className="text-zinc-950 font-medium">{highCount} items</strong> ({totalActionable} total: {mediumCount} medium - {lowCount} low)
				</CardDescription> */}
				<CardDescription>
					<div className="flex items-center gap-4 mt-1">
						<div className="flex items-center gap-1.5">
							<div className={`${styles.some_rounded_thing} bg-red-100 text-red-700`}>
								2
							</div>
							<div className={`${styles.some_rounded_thing} bg-yellow-100 text-yellow-700`}>
								3
							</div>
							<div className={`${styles.some_rounded_thing} bg-green-100 text-green-700`}>
								4
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
						<div>New items: <strong className="text-zinc-950 font-medium">{totalActionable}</strong></div>
					</div>
				</CardDescription>
				
			</CardHeader>
			<CardContent className="flex flex-col pr-4 gap-2">
				<div className="flex flex-col gap-2 font-medium">Urgent items</div>
				{/* Top urgent items */}
				<div className="flex flex-col gap-2">
					{topItems.map((item, index) => (
						<div key={index} className="flex items-center gap-2 text-sm bg-white p-2 rounded-md bg-zinc-100">
							{/* <span>{getPriorityIcon(item.priority)}</span> */}
							<span className="font-medium">{item.company}</span>
							<span className="text-gray-600">–</span>
							<span className="text-gray-700">{item.reason}</span>
						</div>
					))}
				</div>

				{/* Summary figures */}
				{/* <div className="text-sm text-gray-600 border-t pt-3">
					<span className="font-medium text-zinc-950">Total actionable {totalActionable}</span>
					<span className="mx-2">–</span>
					<span className="text-zinc-950">Medium {mediumCount}</span>
					<span className="mx-2">–</span>
					<span className="text-zinc-950">Low {lowCount}</span>
				</div> */}

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
