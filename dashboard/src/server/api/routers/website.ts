import { TRPCError } from '@trpc/server';
import { startOfDay, endOfDay } from 'date-fns';
import { and, count, gte, lt, eq, desc } from 'drizzle-orm';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { website, processed_GET_schema, processed_DELETE_by_id_schema, processed_DELETE_schema } from '~/server/db/schema';

import { processedWebsitesSchema } from '~/server/db/schemas/validation-schemas';
import { processedItems } from '~/server/db/schemas/processed-items';


export const website_router = createTRPCRouter({
	create: publicProcedure
		.input(processedWebsitesSchema)
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
				const [processedItem] = await tx.insert(processedItems).values({
					type: 'website',
					clientName: input.client_name,
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
					processedItemId: processedItem.id,
					url,
					title,
					content,
					opportunityType: opportunity_type,
					read,
					scrapedAt: scraped_at,
					suggestedAction: suggested_action,
					shortDescription: short_description,
					relevance,
					suggestedReply: suggested_reply
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
					id: processedItems.id,
					client_name: processedItems.clientName,
					actionable: processedItems.actionable,
					created_at: processedItems.createdAt,
					// website columns
					url: website.url,
					title: website.title,
					content: website.content,
					opportunity_type: website.opportunityType,
					read: website.read,
					scraped_at: website.scrapedAt,
					suggested_action: website.suggestedAction,
					short_description: website.shortDescription,
					relevance: website.relevance,
					suggested_reply: website.suggestedReply
				})
				.from(processedItems)
				.innerJoin(website, eq(website.processedItemId, processedItems.id))
				.where(
					input.client_name
						? and(
							eq(processedItems.type, 'website'),
							eq(processedItems.clientName, input.client_name)
						)
						: eq(processedItems.type, 'website')
				)
				.orderBy(desc(processedItems.createdAt))
				.limit(limit);
		}),

	get_today_count: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());
		const todayEnd = endOfDay(new Date());

		const website_count_data = await ctx.db
			.select({ count: count() })
			.from(website)
			.innerJoin(processedItems, eq(website.processedItemId, processedItems.id))
			.where(
				and(
					eq(processedItems.type, 'website'),
					gte(processedItems.createdAt, todayStart),
					lt(processedItems.createdAt, todayEnd),
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
			const results = await ctx.db.delete(processedItems).where(
				input.client_name
					? and(
						eq(processedItems.type, 'website'),
						eq(processedItems.clientName, input.client_name)
					)
					: eq(processedItems.type, 'website')
			).returning();

			return results.length === 0 ? 'no items found' : `${results.length} item(s) deleted`;
		}),

	delete_one: publicProcedure
		.input(processed_DELETE_by_id_schema)
		.mutation(async ({ ctx, input }) => {
			// Delete just the processed_item - CASCADE will delete the email record
			const results = await ctx.db.delete(processedItems).where(eq(processedItems.id, input.id)).returning();

			return results.length === 0 ? 'item not found' : 'item deleted';
		})
});
