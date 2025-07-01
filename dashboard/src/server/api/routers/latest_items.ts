import z from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { fetch_latest_items, fetch_latest_items_by_type } from '~/server/db/fetch_items';
import { processedItemTypeEnum } from '~/server/db/schema';

export const processed_items_router = createTRPCRouter({
	getLatest: publicProcedure
		.input(z.object({
			limit: z.number().min(1).default(10),
			actionable: z.boolean().default(false),
		}))
		.query(async ({ input }) => {
			const { limit, actionable } = input;

			const items = await fetch_latest_items({
				limit,
				actionable
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