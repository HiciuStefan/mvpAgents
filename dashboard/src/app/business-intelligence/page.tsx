import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";
import { ClientSelect } from "~/components/filters/ClientSelect";
import { ChannelSelect } from "~/components/filters/ChannelSelect";
import { DateFilter } from "~/components/filters/DateFilter";



export default async function BusinessIntelligence()
{
	const latest_items = await api.processed_items.getLatest({
		limit: 100,
		actionable: true
	});
	const clientOptions = Array.from(new Set(latest_items.map(item => item.client_name)));

	return (
		<div className="flex flex-col align-middle p-20 pt-8 font-[family-name:var(--font-geist-sans)]">
			<h1 className="text-2xl font-semibold text-[26px]">Business Intelligence</h1>
			<p className="text-zinc-500 text-[17px] mb-8">
				Focus on what matters most with filtered insights for smarter business decisions.
			</p>
			<div className="flex space-x-4 mb-8">
				<ClientSelect clients={clientOptions} />
				<ChannelSelect />
				<DateFilter />
			</div>
			<main className="flex w-5xl flex-col gap-[16px]">
				{latest_items.map((item, index) => {
					return (
						<ItemCard key={index} item={item} />
					);
				})}
			</main>
		</div>
	);
}

