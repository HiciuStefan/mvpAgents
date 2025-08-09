import { TRPCError } from '@trpc/server';
import { startOfDay, endOfDay } from 'date-fns';
import { and, count, gte, lt, eq, desc } from 'drizzle-orm';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { processed_items, processed_tweets_schema, twitter, processed_GET_schema, processed_DELETE_by_id_schema, processed_DELETE_schema } from '~/server/db/schema';

export const twitter_router = createTRPCRouter({
	create: publicProcedure
		.input(processed_tweets_schema)
		.mutation(async ({ ctx, input }) => {
			return await ctx.db.transaction(async (tx) => {
				const existing = await tx
					.select()
					.from(twitter)
					.where(
						eq(twitter.tweet_id, input.tweet_id)
					)
					.limit(1);

				if (existing.length > 0) {
					throw new TRPCError({
						code: 'CONFLICT',
						message: 'Tweet ID already processed',
					});
				}

				const [processedItem] = await tx.insert(processed_items).values({
					type: 'twitter',
					client_name: input.client_name,
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
					processed_item_id: processedItem.id,
					tweet_id,
					url,
					text,
					suggested_reply,
					suggested_action,
					short_description,
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
					id: processed_items.id,
					client_name: processed_items.client_name,
					actionable: processed_items.actionable,
					created_at: processed_items.created_at,
					// twitter columns
					tweet_id: twitter.tweet_id,
					url: twitter.url,
					text: twitter.text,
					suggested_reply: twitter.suggested_reply,
					suggested_action: twitter.suggested_action,
					short_description: twitter.short_description,
					relevance: twitter.relevance
				})
				.from(processed_items)
				.innerJoin(twitter, eq(twitter.processed_item_id, processed_items.id))
				.where(
					input.client_name
						? and(
							eq(processed_items.type, 'twitter'),
							eq(processed_items.client_name, input.client_name)
						)
						: eq(processed_items.type, 'twitter')
				)
				.orderBy(desc(processed_items.created_at))
				.limit(limit);
		}),

	getLatest2: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());

		const data = await ctx.db
			.select()
			.from(twitter)
			.innerJoin(processed_items, eq(twitter.processed_item_id, processed_items.id))
			.where(
				and(
					eq(processed_items.type, 'twitter'),
					gte(processed_items.created_at, todayStart)
				)
			)
			.orderBy(desc(processed_items.created_at));

		return data;
	}),

	get_today_count: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());
		const todayEnd = endOfDay(new Date());

		const twitter_count_data = await ctx.db
			.select({ count: count() })
			.from(twitter)
			.innerJoin(processed_items, eq(twitter.processed_item_id, processed_items.id))
			.where(
				and(
					eq(processed_items.type, 'twitter'),
					gte(processed_items.created_at, todayStart),
					lt(processed_items.created_at, todayEnd),
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
			const results = await ctx.db.delete(processed_items).where(
				input.client_name
					? and(
						eq(processed_items.type, 'twitter'),
						eq(processed_items.client_name, input.client_name)
					)
					: eq(processed_items.type, 'twitter')
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
