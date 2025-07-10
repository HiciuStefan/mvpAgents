'use client';

import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";

export async function ClientIntelligenceContent()
{
	const latest_items = await api.processed_items.getLatest({
		limit: 100
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