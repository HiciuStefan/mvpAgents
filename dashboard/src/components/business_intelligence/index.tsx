import Link from "next/link";
import { Button } from "~/components/ui/button"
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "~/components/ui/card";

import styles from "./styles.module.css";
import { ROUTES } from "~/lib/nav_items";


type BusinessIntelligenceType = {
	name: string;
	description: string;
}

const mock_data : BusinessIntelligenceType[] = [{
	name: 'Acme Comp',
	description: 'Sarah Johnson, CEO'
}, {
	name: 'Globex Inc',
	description: 'Sarah Lee started a new job'
}, {
	name: 'Initech',
	description: 'Mentioned by news outlet'
}]





async function fetchMockData(): Promise<BusinessIntelligenceType[]> {
	return new Promise((resolve) => {
		resolve(mock_data);
	});
}


export async function BusinessIntelligence()
{
	const data = await fetchMockData();


	return (
		<Card className={styles.card}>
			<CardHeader>
				<CardTitle className={styles.card_title}>Business Intelligence</CardTitle>
			</CardHeader>
			<CardContent className="flex flex-col pr-4 gap-6">
				<div className="flex flex-col pr-4 gap-2">
					{data.map((item, index) => {
						return (
							<div key={index}>
								{item.name} {item.description}
							</div>
						)
					})}
				</div>
				<Button className="w-full" variant="outline" asChild>
					<Link href={ROUTES.BUSINESS_INTELLIGENCE}>
						View updates
					</Link>
				</Button>
			</CardContent>
		</Card>
	);
}