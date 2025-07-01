import Link from "next/link";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "~/components/ui/card";

import { Progress } from "~/components/ui/progress";

import styles from "./styles.module.css";


type mock_data = {
	email_count: number;
	linkedin_count: number;
	xcom_count: number;
};

const mock_data = {
	email_count: 120,
	linkedin_count: 60,
	xcom_count: 55,
}


async function fetchMockData(): Promise<mock_data> {
	return new Promise((resolve) => {
		resolve(mock_data);
	});
}


export async function DailyUpdates()
{
	const data = await fetchMockData();

	const { email_count, linkedin_count, xcom_count } = data;

	const total = email_count + linkedin_count + xcom_count;

	return (
		<Card className={styles.card}>
			<CardHeader>
				<CardTitle className={styles.card_title}>Daily Updates</CardTitle>
			</CardHeader>
			<CardContent className="pr-4">
				<div className="flex items-start gap-5">
					<span className="font-display text-3xl lg:text-4xl font-bold">{total}</span>
					<ProgressBars data={data} />
				</div>
			</CardContent>
		</Card>
	);
}


function ProgressBars({ data } : { data : mock_data })
{
	const { email_count, linkedin_count, xcom_count } = data;
	const total = email_count + linkedin_count + xcom_count;

	return (
		<div className="flex flex-col mt-[-10px] gap-1 w-full">
			<div>
				<Link href="/latest-items/email" className={styles.item_link}>
					<div className="flex justify-between">
						<span>Email</span>
						<span>{email_count}</span>
					</div>
					<Progress value={Math.round((100 * email_count) / total)} className="[&>div]:bg-[#369ce5]" />
				</Link>
			</div>
			<div>
				<Link href="/latest-items/website" className={styles.item_link}>
					<div className="flex justify-between">
						<span>LinkedIn</span>
						<span>{linkedin_count}</span>
					</div>
					<Progress value={Math.round((100 * linkedin_count) / total)} className="[&>div]:bg-[#9187ce]" />
				</Link>
			</div>
			<div>
				<Link href="/latest-items/twitter" className={styles.item_link}>
					<div className="flex justify-between">
						<span>x.com (twitter)</span>
						<span>{xcom_count}</span>
					</div>
					<Progress value={Math.round((100 * xcom_count) / total)} className="[&>div]:bg-[#a3cf87]" />
				</Link>
			</div>
		</div>
	)
}