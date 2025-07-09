import Link from "next/link";
import { Button } from "~/components/ui/button"
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	CardDescription,
} from "~/components/ui/card";

import styles from "./styles.module.css";
import { ROUTES } from "~/lib/nav_items";

type UrgentActionableType = {
	company: string;
	reason: string;
	priority: 'high' | 'medium' | 'low';
	channel: 'email' | 'social' | 'whatsapp' | 'notes';
	overdueDuration?: string;
}

const mock_data: UrgentActionableType[] = [
	{
		company: 'Umbrella Corp',
		reason: 'SLA overdue 36 h',
		priority: 'high',
		channel: 'email'
	},
	{
		company: 'Initech',
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
		channel: 'social'
	},
	{
		company: 'Wayne Enterprises',
		reason: 'Budget approval needed',
		priority: 'medium',
		channel: 'notes'
	},
	{
		company: 'Stark Industries',
		reason: 'Technical review',
		priority: 'low',
		channel: 'social'
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
		channel: 'notes'
	},
	{
		company: 'InGen',
		reason: 'Status report',
		priority: 'low',
		channel: 'whatsapp'
	}
];

async function fetchMockData(): Promise<UrgentActionableType[]> {
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

function getChannelIcon(channel: 'email' | 'social' | 'whatsapp' | 'notes'): string {
	switch (channel) {
		case 'email': return '✉';
		case 'social': return '🐦';
		case 'whatsapp': return '𝖶';
		case 'notes': return '🗒';
		default: return '📄';
	}
}

export async function UrgentActionablesBackup() {
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
	}, {} as Record<string, number>);

	// Get top 2 items to display
	const topItems = [
		...highPriorityItems.slice(0, 2),
		...mediumPriorityItems.slice(0, Math.max(0, 2 - highPriorityItems.length))
	].slice(0, 2);

	return (
		<Card className={styles.card}>
			<CardHeader>
				<CardTitle className={styles.card_title}>
					Business Intelligence
				</CardTitle>
				<CardDescription>
					Urgent Actionables: <strong className="text-zinc-950 font-medium">{highCount} items</strong>
				</CardDescription>
			</CardHeader>
			<CardContent className="flex flex-col pr-4 gap-4">
				{/* Top urgent items */}
				<div className="flex flex-col gap-2">
					{topItems.map((item, index) => (
						<div key={index} className="flex items-center gap-2 text-sm">
							<span>{getPriorityIcon(item.priority)}</span>
							<span className="font-medium">{item.company}</span>
							<span className="text-gray-600">–</span>
							<span className="text-gray-700">{item.reason}</span>
						</div>
					))}
				</div>

				{/* Summary figures */}
				<div className="text-sm text-gray-600 border-t pt-3">
					<span className="font-medium">Total actionable {totalActionable}</span>
					<span className="mx-2">│</span>
					<span>Medium {mediumCount}</span>
					<span className="mx-2">│</span>
					<span>Low {lowCount}</span>
				</div>

				{/* Channel badges */}
				<div className="flex items-center gap-3 text-sm">
					{Object.entries(channelCounts).map(([channel, count]) => (
						<span key={channel} className="flex items-center gap-1">
							{getChannelIcon(channel as 'email' | 'social' | 'whatsapp' | 'notes')}<span>{count}</span>
						</span>
					))}
				</div>

				<Button className="w-full" variant="outline" asChild>
					<Link href={ROUTES.BUSINESS_INTELLIGENCE}>
						View all actionables
					</Link>
				</Button>
			</CardContent>
		</Card>
	);
}