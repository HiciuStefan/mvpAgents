import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";
import { ClientSelect } from "~/components/filters/ClientSelect";
import { ChannelSelect } from "~/components/filters/ChannelSelect";
import { DateFilter } from "~/components/filters/DateFilter";
import styles from "./styles.module.css";
import { fetchMockData } from "~/components/urgent_actionables";




export default async function BusinessIntelligence()
{
	const data = await fetchMockData();
	const totalActionable = data.length;

	const latest_items = await api.processed_items.getLatest({
		limit: 100,
		actionable: true
	});

	const clientOptions = Array.from(new Set(latest_items.map(item => item.client_name)));

	return (
		<div className="flex flex-col align-middle p-20 pt-8 font-[family-name:var(--font-geist-sans)]">
			<h1 className="text-2xl font-semibold text-[26px]">Business Intelligence</h1>
			<p className="text-zinc-500 text-[17px] mb-6">
				Focus on what matters most with filtered insights for smarter business decisions.
			</p>
			<div className="flex space-x-4 mb-8">
				<ClientSelect clients={clientOptions} />
				<ChannelSelect />
				<DateFilter />
			</div>
			<div className="flex items-center gap-1 mt-1 mb-3.5">
				<div className={`${styles.rounded_rectangle} bg-red-100 text-red-700 hover:bg-[#ffd5d5]`}>
					High 2
				</div>
				<div className={`${styles.rounded_rectangle} bg-yellow-100 text-yellow-700 hover:bg-[#fff4a3]`}>
					Medium 3
				</div>
				<div className={`${styles.rounded_rectangle} bg-green-100 text-green-700 hover:bg-[#cafadb]`}>
					Low 4
				</div>
				<div className={`${styles.rounded_rectangle} bg-gray-100 text-gray-600 hover:bg-[#ecedf0]`}>
					New&nbsp;<strong className="text-zinc-950 font-medium"> {totalActionable}</strong>
				</div>
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
