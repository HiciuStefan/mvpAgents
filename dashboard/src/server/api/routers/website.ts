import { TRPCError } from '@trpc/server';
import { startOfDay, endOfDay } from 'date-fns';
import { and, count, gte, lt, eq, desc } from 'drizzle-orm';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { processed_websites_schema, website, processed_GET_schema, processed_items, processed_DELETE_by_id_schema, processed_DELETE_schema } from '~/server/db/schema';



export const website_router = createTRPCRouter({
	create: publicProcedure
		.input(processed_websites_schema)
		.mutation(async ({ ctx, input }) => {
			return await ctx.db.transaction(async (tx) => {
				// Check if URL already processed
				const existing = await tx
					.select()
					.from(website)
					.where(
						eq(website.url, input.url)
					)
					.limit(1);

				if (existing.length > 0) {
					throw new TRPCError({
						code: 'CONFLICT',
						message: 'URL already processed',
					});
				}

				// Create processed_items record with actionable field
				const [processedItem] = await tx.insert(processed_items).values({
					type: 'website',
					client_name: input.client_name,
					actionable: input.actionable,
					urgency: input.urgency
				}).returning();

				if (!processedItem) {
					throw new Error('Failed to insert processed item');
				}

				// Extract all fields from input for website table
				const {
					url,
					title,
					content,
					opportunity_type,
					read,
					scraped_at,
					suggested_action,
					short_description,
					relevance,
					suggested_reply
				} = input;

				const [item] = await tx.insert(website).values({
					processed_item_id: processedItem.id,
					url,
					title,
					content,
					opportunity_type,
					read,
					scraped_at,
					suggested_action,
					short_description,
					relevance,
					suggested_reply
				}).returning();

				return {
					processedItem,
					item,
				};
			});
		}),

	getLatest: publicProcedure
		.input(processed_GET_schema)
		.query(async ({ ctx, input }) => {
			const limit = input?.limit ?? 1;

			return await ctx.db
				.select({
					// processed_items columns
					id: processed_items.id,
					client_name: processed_items.client_name,
					actionable: processed_items.actionable,
					created_at: processed_items.created_at,
					// website columns
					url: website.url,
					title: website.title,
					content: website.content,
					opportunity_type: website.opportunity_type,
					read: website.read,
					scraped_at: website.scraped_at,
					suggested_action: website.suggested_action,
					short_description: website.short_description,
					relevance: website.relevance,
					suggested_reply: website.suggested_reply
				})
				.from(processed_items)
				.innerJoin(website, eq(website.processed_item_id, processed_items.id))
				.where(
					input.client_name
						? and(
							eq(processed_items.type, 'website'),
							eq(processed_items.client_name, input.client_name)
						)
						: eq(processed_items.type, 'website')
				)
				.orderBy(desc(processed_items.created_at))
				.limit(limit);
		}),

	get_today_count: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());
		const todayEnd = endOfDay(new Date());

		const website_count_data = await ctx.db
			.select({ count: count() })
			.from(website)
			.innerJoin(processed_items, eq(website.processed_item_id, processed_items.id))
			.where(
				and(
					eq(processed_items.type, 'website'),
					gte(processed_items.created_at, todayStart),
					lt(processed_items.created_at, todayEnd),
				),
			);

		const website_count = website_count_data[0]

		if (website_count === undefined) {
			return 0;
		}

		return website_count.count ?? 0
	}),

	delete_all: publicProcedure
		.input(processed_DELETE_schema)
		.mutation(async ({ ctx, input }) => {
			const results = await ctx.db.delete(processed_items).where(
				input.client_name
					? and(
						eq(processed_items.type, 'website'),
						eq(processed_items.client_name, input.client_name)
					)
					: eq(processed_items.type, 'website')
			).returning();

			return results.length === 0 ? 'no items found' : `${results.length} item(s) deleted`;
		}),

	delete_one: publicProcedure
		.input(processed_DELETE_by_id_schema)
		.mutation(async ({ ctx, input }) => {
			// Delete just the processed_item - CASCADE will delete the email record
			const results = await ctx.db.delete(processed_items).where(eq(processed_items.id, input.id)).returning();

			return results.length === 0 ? 'item not found' : 'item deleted';
		})
});
