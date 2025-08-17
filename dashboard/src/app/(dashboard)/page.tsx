import { api, HydrateClient } from "~/trpc/server";


import { ActionableItems } from "~/components/actionable_items";
import { BusinessIntelligence } from "~/components/business_intelligence";
import { LatestProcessed } from "~/components/latest_processed";
import { CenteredDailyUpdates } from "~/components/daily_updates/centered";
import Header from "~/components/header";
import { UrgentActionables } from "~/components/urgent_actionables";
// import BusinessIntelligenceCard2 from "./something";


export default async function Home()
{
	void api.email.get_today_count.prefetch();
	void api.twitter.get_today_count.prefetch();
	void api.website.get_today_count.prefetch();


	const email_count   = await api.email.get_today_count();
	const twitter_count = await api.twitter.get_today_count();
	const website_count = await api.website.get_today_count();

	const daily_data = {
		email_count,
		twitter_count,
		website_count,
	};

	const actionable_data = {
		email_count,
		task_count: 5,
		notes_count: 4,
	}


	return (
		<HydrateClient>
			<div className="flex w-full justify-center align-top pb-16 pt-21 px-4 font-[family-name:var(--font-geist-sans)]">
				<main className="flex flex-col gap-[24px]">
					<Header />
					<div className="flex flex-row gap-[24px]">
						<div className="flex flex-col gap-[24px]">
							<CenteredDailyUpdates data={daily_data} />
							<ActionableItems data={actionable_data} />
						</div>
						<div className="flex flex-col gap-[24px]">
							<div className="flex flex-row gap-[24px]">
								{/* <BusinessIntelligence />
								 */}
								{/* <UrgentActionables /> */}
								<LatestProcessed />
								{/* <ActionableItems data={actionable_data} /> */}
							</div>
							<UrgentActionables />
							{/* <BusinessIntelligenceCard2 /> */}
							{/* <LatestProcessed /> */}
						</div>
					</div>
				</main>
			</div>
		</HydrateClient>
	);
}





