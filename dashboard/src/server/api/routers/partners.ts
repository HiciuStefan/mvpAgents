import { z } from 'zod';
import { createTRPCRouter, authenticatedProcedure } from '~/server/api/trpc';
import { partners, partnerFormSchema } from '~/server/db/schemas/partners';
import { eq, desc, and, gte, sql } from 'drizzle-orm';

export const partners_router = createTRPCRouter({
  // Create a new partner
  create: authenticatedProcedure
    .input(partnerFormSchema)
    .mutation(async ({ ctx, input }) => {
      const [newPartner] = await ctx.db
        .insert(partners)
        .values({
          ...input,
          userId: ctx.user.userId,
        })
        .returning();

      return newPartner;
    }),

  // Get all partners for the current user with optional filtering
  getAll: authenticatedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(50),
        offset: z.number().min(0).default(0),
        search: z.string().optional(),
        dateRange: z.enum(['today', 'last_week', 'last_30_days']).optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { limit, offset, search, dateRange } = input;

      // Build where conditions
      const whereConditions = [eq(partners.userId, ctx.user.userId)];

      // Add search filter
      if (search) {
        whereConditions.push(
          // You might want to use a more sophisticated search here
          // For now, we'll search in name and description
          // This is a simple approach - consider using full-text search for production
          eq(partners.name, search)
        );
      }

      // Add date range filter
      if (dateRange) {
        const now = new Date();
        let startDate: Date;

        switch (dateRange) {
          case 'today':
            startDate = new Date(
              now.getFullYear(),
              now.getMonth(),
              now.getDate()
            );
            break;
          case 'last_week':
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
          case 'last_30_days':
            startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
          default:
            startDate = new Date(0);
        }

        whereConditions.push(gte(partners.createdAt, startDate));
      }

      const results = await ctx.db
        .select()
        .from(partners)
        .where(and(...whereConditions))
        .orderBy(desc(partners.createdAt))
        .limit(limit)
        .offset(offset);

      // Get total count for pagination
      const countResult = await ctx.db
        .select({ count: sql`count(*)` })
        .from(partners)
        .where(and(...whereConditions));

      const count = countResult[0]?.count;

      return {
        partners: results,
        total: Number(count ?? 0),
        hasMore: results.length === limit,
      };
    }),

  // Get a single partner by ID
  getById: authenticatedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const [partner] = await ctx.db
        .select()
        .from(partners)
        .where(
          and(eq(partners.id, input.id), eq(partners.userId, ctx.user.userId))
        );

      if (!partner) {
        throw new Error('Partner not found');
      }

      return partner;
    }),

  // Update a partner
  update: authenticatedProcedure
    .input(
      z.object({
        id: z.string().uuid(),
        data: z.object({
          name: z.string().optional(),
          description: z.string().optional(),
          goals: z.string().optional(),
        }),
      })
    )
    .mutation(async ({ ctx, input }) => {
      // First verify the partner belongs to the current user
      const [existingPartner] = await ctx.db
        .select()
        .from(partners)
        .where(
          and(eq(partners.id, input.id), eq(partners.userId, ctx.user.userId))
        );

      if (!existingPartner) {
        throw new Error('Partner not found');
      }

      const [updatedPartner] = await ctx.db
        .update(partners)
        .set({
          ...input.data,
          updatedAt: new Date(),
          updatedByUserId: ctx.user.userId,
        })
        .where(eq(partners.id, input.id))
        .returning();

      return updatedPartner;
    }),

  // Delete a partner
  delete: authenticatedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ ctx, input }) => {
      // First verify the partner belongs to the current user
      const [existingPartner] = await ctx.db
        .select()
        .from(partners)
        .where(
          and(eq(partners.id, input.id), eq(partners.userId, ctx.user.userId))
        );

      if (!existingPartner) {
        throw new Error('Partner not found');
      }

      await ctx.db.delete(partners).where(eq(partners.id, input.id));

      return { success: true };
    }),

  // Get partners with advanced filtering
  getFiltered: authenticatedProcedure
    .input(
      z.object({
        channel: z.enum(['all', 'website', 'email', 'twitter']).optional(),
        dateRange: z.enum(['today', 'last_week', 'last_30_days']).optional(),
        clientName: z.string().optional(),
        limit: z.number().min(1).max(100).default(50),
        offset: z.number().min(0).default(0),
      })
    )
    .query(async ({ ctx, input }) => {
      const { dateRange, clientName, limit, offset } = input;

      // Build where conditions
      const whereConditions = [eq(partners.userId, ctx.user.userId)];

      // Add client name filter
      if (clientName && clientName !== 'all') {
        whereConditions.push(eq(partners.name, clientName));
      }

      // Add date range filter
      if (dateRange && dateRange !== 'today') {
        const now = new Date();
        let startDate: Date;

        switch (dateRange) {
          case 'last_week':
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
          case 'last_30_days':
            startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
          default:
            startDate = new Date(0);
        }

        whereConditions.push(gte(partners.createdAt, startDate));
      }

      const results = await ctx.db
        .select()
        .from(partners)
        .where(and(...whereConditions))
        .orderBy(desc(partners.createdAt))
        .limit(limit)
        .offset(offset);

      // Get total count for pagination
      const countResult = await ctx.db
        .select({ count: sql`count(*)` })
        .from(partners)
        .where(and(...whereConditions));

      const count = countResult[0]?.count;

      return {
        partners: results,
        total: Number(count ?? 0),
        hasMore: results.length === limit,
      };
    }),
});
