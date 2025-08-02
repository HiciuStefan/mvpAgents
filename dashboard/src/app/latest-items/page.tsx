import { Suspense } from "react";
import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";


export default async function ClientIntelligence()
{
	return (
		<div className="flex flex-col align-middle p-20 pt-8 font-[family-name:var(--font-geist-sans)]">
			<h1 className="text-2xl font-semibold text-[26px]">Latest items</h1>
			<p className="text-zinc-500 text-[17px] mb-8">
				View all the latest processed items
			</p>
			<main className="flex w-5xl flex-col gap-[16px]">
				<Suspense fallback={<ClientSkeleton />}>
					<ClientIntelligenceContent />
				</Suspense>
			</main>
		</div>
	);
}


async function ClientIntelligenceContent()
{
	const latest_items = await api.processed_items.getLatest({
		limit: 100,
		channel: 'all',
		date_range: 'last_30_days'
	});

	return (
		<>
			{latest_items.map((item, index) => {
				return (
					<ItemCard key={index} item={item} />
				);
			})}
		</>
	);
}


function ClientSkeleton()
{
	return (
		<>
			{Array.from({ length: 5 }).map((_, index) => (
				<div key={index} className="animate-pulse bg-gray-100 h-35 w-full rounded-2xl mb-1" />
			))}
		</>
	);
}