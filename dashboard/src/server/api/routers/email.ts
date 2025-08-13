import { TRPCError } from '@trpc/server';
import { startOfDay, endOfDay } from 'date-fns';
import { and, count, gte, lt, eq, desc } from 'drizzle-orm';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { email, processed_DELETE_by_id_schema, processed_DELETE_schema, processed_emails_schema, processed_GET_schema, processed_items } from '~/server/db/schema';

export const email_router = createTRPCRouter({
	create: publicProcedure
		.input(processed_emails_schema)
		.mutation(async ({ ctx, input }) => {
			const result = await ctx.db.transaction(async (tx) => {
				const existing = await tx
					.select()
					.from(email)
					.where(
						eq(email.message_id, input.message_id)
					)
					.limit(1);

				if (existing.length > 0) {
					throw new TRPCError({
						code: 'CONFLICT',
						message: 'Message ID already processed',
					});
				}

				const [processedItem] = await tx.insert(processed_items).values({
					type: 'email',
					client_name: input.client_name,
					actionable: input.actionable,
					urgency: input.urgency
				}).returning();

				if (!processedItem) {
					throw new Error('Failed to insert processed item');
				}

				const {
					message_id,
					subject,
					content,
					type,
					processed_at,
					suggested_action,
					short_description,
					relevance,
					suggested_reply
				} = input;

				const [item] = await tx.insert(email).values({
					processed_item_id: processedItem.id,
					message_id,
					subject,
					content,
					type,
					processed_at,
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

			return result;
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
					// email columns
					message_id: email.message_id,
					subject: email.subject,
					content: email.content,
					type: email.type,
					processed_at: email.processed_at,
					suggested_action: email.suggested_action,
					short_description: email.short_description,
					relevance: email.relevance,
					suggested_reply: email.suggested_reply
				})
				.from(processed_items)
				.innerJoin(email, eq(email.processed_item_id, processed_items.id))
				.where(
					input.client_name
						? and(
							eq(processed_items.type, 'email'),
							eq(processed_items.client_name, input.client_name)
						)
						: eq(processed_items.type, 'email')
				)
				.orderBy(desc(processed_items.created_at))
				.limit(limit);
		}),

	get_today_count: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());
		const todayEnd   = endOfDay(new Date());

		const email_count_data = await ctx.db
			.select({ count: count() })
			.from(email)
			.innerJoin(processed_items, eq(email.processed_item_id, processed_items.id))
			.where(
				and(
					eq(processed_items.type, 'email'),
					gte(processed_items.created_at, todayStart),
					lt(processed_items.created_at, todayEnd),
				),
			);

		const email_count = email_count_data[0]

		if (email_count === undefined) {
			return 0;
		}

		return email_count.count ?? 0
	}),

	delete_all: publicProcedure
		.input(processed_DELETE_schema)
		.mutation(async ({ ctx, input }) => {
			const results = await ctx.db.delete(processed_items).where(
				input.client_name
					? and(
						eq(processed_items.type, 'email'),
						eq(processed_items.client_name, input.client_name)
					)
					: eq(processed_items.type, 'email')
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
