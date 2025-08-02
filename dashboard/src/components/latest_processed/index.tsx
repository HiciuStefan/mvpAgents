import Link from "next/link";
import { Button } from "~/components/ui/button"
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "~/components/ui/card";
import { api } from "~/trpc/server";

import styles from "./styles.module.css";



import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "~/components/ui/table"
import { ROUTES } from "~/lib/nav_items";
import { DefaultChannelValue } from "../filters/channel_ranges";



function get_display_type(type: string)
{
	if (type === 'twitter') return 'X (twitter)';
	if (type === 'email')   return 'Email';
	if (type === 'website') return 'Website';

	return type;
}

export async function LatestProcessed()
{
	const latest_items = await api.processed_items.getLatest({
		limit: 4,
		channel: DefaultChannelValue,
		date_range: 'last_30_days'
	});

	return (
		<Card className="w-full gap-4">
			<CardHeader>
				<CardTitle className={styles.card_title}>Latest</CardTitle>
			</CardHeader>
			<CardContent className="flex flex-col pr-4 gap-6">
				<div className="flex flex-col pr-4 gap-3">
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead className="w-[100px]">Channel</TableHead>
								<TableHead>Description</TableHead>
								<TableHead>Company</TableHead>
								<TableHead className="text-right">Action Type</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{latest_items.map((item, index) => {
								const { type, data, actionable, client_name } = item;

								const { short_description } = data;

								const action_type = actionable ? 'Actionable' : 'Informative';

								return (
									<TableRow key={index}>
										<TableCell className="font-medium">{get_display_type(type)}</TableCell>
										<TableCell>{short_description}</TableCell>
										<TableCell>{client_name}</TableCell>
										<TableCell className="text-right">{action_type}</TableCell>
									</TableRow>
								)
							})}
						</TableBody>
					</Table>
				</div>
				<Button className="w-full" variant="outline" asChild>
					<Link href={ROUTES.LATEST_ITEMS}>
						View All
					</Link>
				</Button>
			</CardContent>
		</Card>
	);
}