import { notFound } from "next/navigation";
import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";
import { processedItemTypeEnum, type ProcessedItemType } from "~/server/db/schema";



export const dynamic = 'force-dynamic';

export default async function LatestItemsByType({
	params,
}: {
	params: Promise<{ type: string }>
}) {
	const { type } = await params;

	// Validate the type parameter
	if (processedItemTypeEnum.enumValues.includes(type as ProcessedItemType) === false) {
		notFound();
	}

	const validatedType = type as ProcessedItemType;

	try {
		// Fetch latest items for the specific type
		const latest_items = await api.processed_items.getLatestByType({
			type: validatedType,
			limit: 100
		});

		return (
			<div className="flex align-middle p-20 font-[family-name:var(--font-geist-sans)]">
				<main className="flex w-5xl flex-col gap-[16px]">
					<h1 className="text-2xl font-bold mb-4 capitalize">
						Latest {validatedType} Items
					</h1>
					{latest_items.length === 0 ? (
						<p className="text-gray-500">No {validatedType} items found.</p>
					) : (
						latest_items.map((item, index) => (
							<ItemCard key={index} item={item} />
						))
					)}
				</main>
			</div>
		);
	} catch (error) {
		console.error("Error fetching latest items:", error);
		notFound();
	}
}