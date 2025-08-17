'use client'

import { PriorityFilter, type Priorities } from "~/components/filters/PriorityFilter";
import type { LatestItem } from "~/server/db/fetch_items";
import { ItemCard } from "~/components/cards/ItemCard";
import { useUrgencyFilter } from "~/hooks/use-urgency-filter";

export default function BusinessIntelligenceClient({
	items,
	priorities,
}: {
	items: LatestItem[];
	priorities: Priorities;
}) {
	const { filter, setFilter } = useUrgencyFilter();

	const filtered_items_w_priority = items.filter(item => {
		if (filter !== null) {
			return item.urgency === filter;
		}
		return true;
	});

	return (
		<>
			<div className="flex items-center gap-1 mt-1 mb-3.5">
				<PriorityFilter priorities={priorities} filter={filter} setFilter={setFilter} />
			</div>
			<main className="flex w-5xl flex-col gap-[16px]">
				{filtered_items_w_priority.map((item, index) => {
					return (
						<ItemCard key={index} item={item} />
					);
				})}
			</main>
		</>
	);
}
