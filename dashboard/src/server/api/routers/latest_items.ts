import z from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { fetch_latest_items, fetch_latest_items_by_type, fetch_item_by_id } from '~/server/db/fetch_items';
import { processedItemTypeEnum } from '~/server/db/schema';
import { dateRangeValues, zodDateRangeEnum } from '~/components/filters/date_ranges';
import { zodChannelEnum } from '~/components/filters/channel_ranges';
import { eq } from 'drizzle-orm';
import { processedItems } from '~/server/db/schema';
import { revalidatePath } from 'next/cache';



const prioritySchema = z.union([
	z.literal("all"),
	z.number().int().min(1).max(3),
]);

export const processed_items_router = createTRPCRouter({
	getLatest: publicProcedure
		.input(z.object({
			limit: z.number().min(1).default(10),
			actionable: z.boolean().default(false),
			date_range: zodDateRangeEnum,
			channel: zodChannelEnum,
			// priority: prioritySchema
		}))
		.query(async ({ input }) => {
			const { limit, actionable, date_range, channel
				// , priority
			 } = input;

			const items = await fetch_latest_items({
				limit,
				actionable,
				date_range,
				channel,
				// priority
			});

			return items;
		}),

	getLatestAvailable: publicProcedure
		.input(z.object({
			limit: z.number().min(1).default(10),
			actionable: z.boolean().default(false),
			channel: zodChannelEnum,
			// priority: prioritySchema
		}))
		.query(async ({ input }) => {
			const { limit, actionable, channel /* , priority */ } = input;

			for (const range of dateRangeValues) {
				const items = await fetch_latest_items({
					limit,
					actionable,
					date_range: range,
					channel,
					// priority
				});

				if (items && items.length > 0) {
					return items;
				}
			}

			return [];
		}),

	getLatestByType: publicProcedure
		.input(z.object({
			type: z.enum(processedItemTypeEnum.enumValues),
			limit: z.number().min(1).default(10),
			actionable: z.boolean().default(false),
		}))
		.query(async ({ input }) => {
			const { type, limit, actionable } = input;

			const items = await fetch_latest_items_by_type({
				type,
				limit,
				actionable
			});

			return items;
		}),

	getById: publicProcedure
		.input(z.object({ id: z.string().uuid() }))
		.query(async ({ input }) => {
			const item = await fetch_item_by_id(input.id);
			return item;
		}),

	updateUrgency: publicProcedure
		.input(z.object({ id: z.string().uuid(), urgency: z.number().int().min(0).max(3) }))
		.mutation(async ({ ctx, input }) => {
			await ctx.db.update(processedItems)
				.set({ urgency: input.urgency })
				.where(eq(processedItems.id, input.id));

			// Revalidate list pages
			revalidatePath('/business-intelligence');
			revalidatePath('/latest-items', 'layout');
			revalidatePath(`/items/${input.id}`);

			return { success: true };
		}),
});