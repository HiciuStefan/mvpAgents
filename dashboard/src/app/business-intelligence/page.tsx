import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";



export default async function BusinessIntelligence()
{
	const latest_items = await api.processed_items.getLatest({
		limit: 100,
		actionable: true
	});

	return (
		<div className="flex align-middle p-20 pt-21 font-[family-name:var(--font-geist-sans)]">
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

