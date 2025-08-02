import z from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { fetch_latest_items, fetch_latest_items_by_type } from '~/server/db/fetch_items';
import { processedItemTypeEnum } from '~/server/db/schema';
import { zodDateRangeEnum } from '~/components/filters/date_ranges';
import { zodChannelEnum } from '~/components/filters/channel_ranges';

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
});