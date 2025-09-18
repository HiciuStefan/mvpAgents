import { TRPCError } from '@trpc/server';
import { startOfDay, endOfDay } from 'date-fns';
import { and, count, gte, lt, eq, desc } from 'drizzle-orm';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { twitter, processed_GET_schema, processed_DELETE_by_id_schema, processed_DELETE_schema } from '~/server/db/schema';
import { processedTweetsSchema } from '~/server/db/schemas/validation-schemas';
import { processedItems } from '~/server/db/schemas/processed-items';


export const twitter_router = createTRPCRouter({
	create: publicProcedure
		.input(processedTweetsSchema)
		.mutation(async ({ ctx, input }) => {
			return await ctx.db.transaction(async (tx) => {
				const existing = await tx
					.select()
					.from(twitter)
					.where(
						eq(twitter.tweetId, input.tweet_id)
					)
					.limit(1);

				if (existing.length > 0) {
					throw new TRPCError({
						code: 'CONFLICT',
						message: 'Tweet ID already processed',
					});
				}

				const [processedItem] = await tx.insert(processedItems).values({
					type: 'twitter',
					clientName: input.client_name,
					actionable: input.actionable,
					urgency: input.urgency
				}).returning();

				if (!processedItem) {
					throw new Error('Failed to insert processed item');
				}

				const {
					tweet_id,
					url,
					text,
					suggested_reply,
					suggested_action,
					short_description,
					relevance
				} = input;

				const [item] = await tx.insert(twitter).values({
					processedItemId: processedItem.id,
					tweetId: tweet_id,
					url,
					text,
					suggestedReply: suggested_reply,
					suggestedAction: suggested_action,
					shortDescription: short_description,
					relevance
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
					// twitter columns
					tweet_id: twitter.tweetId,
					url: twitter.url,
					text: twitter.text,
					suggested_reply: twitter.suggestedReply,
					suggested_action: twitter.suggestedAction,
					short_description: twitter.shortDescription,
					relevance: twitter.relevance
				})
				.from(processedItems)
				.innerJoin(twitter, eq(twitter.processedItemId, processedItems.id))
				.where(
					input.client_name
						? and(
							eq(processedItems.type, 'twitter'),
							eq(processedItems.clientName, input.client_name)
						)
						: eq(processedItems.type, 'twitter')
				)
				.orderBy(desc(processedItems.createdAt))
				.limit(limit);
		}),

	getLatest2: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());

		const data = await ctx.db
			.select()
			.from(twitter)
			.innerJoin(processedItems, eq(twitter.processedItemId, processedItems.id))
			.where(
				and(
					eq(processedItems.type, 'twitter'),
					gte(processedItems.createdAt, todayStart)
				)
			)
			.orderBy(desc(processedItems.createdAt));

		return data;
	}),

	get_today_count: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());
		const todayEnd = endOfDay(new Date());

		const twitter_count_data = await ctx.db
			.select({ count: count() })
			.from(twitter)
			.innerJoin(processedItems, eq(twitter.processedItemId, processedItems.id))
			.where(
				and(
					eq(processedItems.type, 'twitter'),
					gte(processedItems.createdAt, todayStart),
					lt(processedItems.createdAt, todayEnd),
				),
			);

		const twitter_count = twitter_count_data[0]

		if (twitter_count === undefined) {
			return 0;
		}

		return twitter_count.count ?? 0
	}),

	delete_all: publicProcedure
		.input(processed_DELETE_schema)
		.mutation(async ({ ctx, input }) => {
			const results = await ctx.db.delete(processedItems).where(
				input.client_name
					? and(
						eq(processedItems.type, 'twitter'),
						eq(processedItems.clientName, input.client_name)
					)
					: eq(processedItems.type, 'twitter')
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
