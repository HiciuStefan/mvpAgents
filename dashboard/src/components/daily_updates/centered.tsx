import Link from "next/link";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	CardDescription,
} from "~/components/ui/card";

import { Progress } from "~/components/ui/progress";

import styles from "./styles.module.css";

type CountDataType = {
	email_count: number;
	twitter_count: number;
	website_count: number;
};


export async function CenteredDailyUpdates({
	data
} : {
	data: CountDataType
}) {

	const { email_count, twitter_count, website_count } = data;
	const total = email_count + twitter_count + website_count;

	return (
		<Card className="rounded-xl overflow-hidden w-[360px] flex-shrink-0">
			<CardHeader className="gap-1 bg-white">
				<CardTitle className="text-[22px] font-semibold">
					Daily Updates
				</CardTitle>
				<CardDescription>
					View your engagement across all platforms
				</CardDescription>
			</CardHeader>
			<div className="bg-[linear-gradient(to_bottom,#154dbc_0%_10%,#fff_75%_100%)] rounded-xl px-2 pt-9">
				<div className="pb-9 flex flex-col items-center">
					<span className="text-base text-white font-medium mb-1">Total Updates</span>
					<span className="font-display text-5xl lg:text-6xl font-medium text-white">
						{total}
					</span>
				</div>
				<CardContent className="px-4">
					<div className="w-full bg-white rounded-lg p-4 shadow-[0_0_16px_rgba(0,0,0,0.12)]">
						<ProgressBars data={data} />
					</div>
				</CardContent>
			</div>
		</Card>
	);
}

function ProgressBars({ data }: { data: CountDataType }) {
	const { email_count, twitter_count, website_count } = data;
	const total = email_count + twitter_count + website_count;


	return (
		<div className="flex flex-col gap-3 w-full">
			<div>
				<Link href="/latest-items/email" className={styles.item_link}>
					<div className="flex justify-between">
						<span>Email</span>
						<span>{email_count}</span>
					</div>
					<Progress
						value={Math.round((100 * email_count) / total)}
						className="[&>div]:bg-[#369ce5]"
					/>
				</Link>
			</div>
			{/* <div>
				<Link href="#" className={styles.item_link}>
					<div className="flex justify-between">
						<span>LinkedIn</span>
						<span>{linkedin_total}</span>
					</div>
					<Progress
						value={Math.round((100 * linkedin_total) / total)}
						className="[&>div]:bg-[#9187ce]"
					/>
				</Link>
			</div> */}
			<div>
				<Link href="/latest-items/website" className={styles.item_link}>
					<div className="flex justify-between">
						<span>Website</span>
						<span>{website_count}</span>
					</div>
					<Progress
						value={Math.round((100 * website_count) / total)}
						className="[&>div]:bg-[#9187ce]"
					/>
				</Link>
			</div>
			<div>
				<Link href="/latest-items/twitter" className={styles.item_link}>
					<div className="flex justify-between">
						<span>x.com (twitter)</span>
						<span>{twitter_count}</span>
					</div>
					<Progress
						value={Math.round((100 * twitter_count) / total)}
						className="[&>div]:bg-[#a3cf87]"
					/>
				</Link>
			</div>
		</div>
	);
}
