import { TRPCError } from '@trpc/server';
import { startOfDay, endOfDay } from 'date-fns';
import { and, count, gte, lt, eq, desc } from 'drizzle-orm';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { email, processed_DELETE_by_id_schema, processed_DELETE_schema, processed_GET_schema } from '~/server/db/schema';

import { processedItems } from '~/server/db/schema';
import { processedEmailsSchema } from '~/server/db/schemas/validation-schemas';

export const email_router = createTRPCRouter({
	create: publicProcedure
		.input(processedEmailsSchema)
		.mutation(async ({ ctx, input }) => {
			const result = await ctx.db.transaction(async (tx) => {
				const existing = await tx
					.select()
					.from(email)
					.where(
						eq(email.messageId, input.message_id)
					)
					.limit(1);

				if (existing.length > 0) {
					throw new TRPCError({
						code: 'CONFLICT',
						message: 'Message ID already processed',
					});
				}

				const [processedItem] = await tx.insert(processedItems).values({
					type: 'email',
					clientName: input.client_name,
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
					processedItemId: processedItem.id,
					messageId : message_id,
					subject,
					content,
					type,
					processedAt: processed_at,
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

			return result;
		}),

	getLatest: publicProcedure
		.input(processed_GET_schema)
		.query(async ({ ctx, input }) => {
			const limit = input?.limit ?? 1;

			return await ctx.db
				.select({
					// processed_items columns
					id: processedItems.id,
					clientName: processedItems.clientName,
					actionable: processedItems.actionable,
					createdAt: processedItems.createdAt,
					// email columns
					messageId: email.messageId,
					subject: email.subject,
					content: email.content,
					type: email.type,
					processedAt: email.processedAt,
					suggestedAction: email.suggestedAction,
					shortDescription: email.shortDescription,
					relevance: email.relevance,
					suggestedReply: email.suggestedReply
				})
				.from(processedItems)
				.innerJoin(email, eq(email.processedItemId, processedItems.id))
				.where(
					input.client_name
						? and(
							eq(processedItems.type, 'email'),
							eq(processedItems.clientName, input.client_name)
						)
						: eq(processedItems.type, 'email')
				)
				.orderBy(desc(processedItems.createdAt))
				.limit(limit);
		}),

	get_today_count: publicProcedure.query(async ({ ctx }) => {
		const todayStart = startOfDay(new Date());
		const todayEnd   = endOfDay(new Date());

		const email_count_data = await ctx.db
			.select({ count: count() })
			.from(email)
			.innerJoin(processedItems, eq(email.processedItemId, processedItems.id))
			.where(
				and(
					eq(processedItems.type, 'email'),
					gte(processedItems.createdAt, todayStart),
					lt(processedItems.createdAt, todayEnd),
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
			const results = await ctx.db.delete(processedItems).where(
				input.client_name
					? and(
						eq(processedItems.type, 'email'),
						eq(processedItems.clientName, input.client_name)
					)
					: eq(processedItems.type, 'email')
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
