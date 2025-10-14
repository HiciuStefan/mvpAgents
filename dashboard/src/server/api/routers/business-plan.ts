import { createTRPCRouter, authenticatedProcedure } from '~/server/api/trpc';
import { businessPlanSchema } from '~/server/db/schemas/business-plan';
import { companyDetails } from '~/server/db/schemas/company-details';
import { users } from '~/server/db/schemas/users';
import { eq } from 'drizzle-orm';

export const businessPlanRouter = createTRPCRouter({
  // Get business plan for the current user
  get: authenticatedProcedure.query(async ({ ctx }) => {
    // First find the user by clerk_id
    const user = await ctx.db
      .select()
      .from(users)
      .where(eq(users.clerk_id, ctx.auth.userId))
      .limit(1);

    if (!user[0]) {
      return null;
    }

    // Then get business plan data from company details using the user's UUID
    const result = await ctx.db
      .select({
        businessOverview: companyDetails.businessOverview,
        companyGoals: companyDetails.companyGoals,
        otherBusinessDetails: companyDetails.otherBusinessDetails,
      })
      .from(companyDetails)
      .where(eq(companyDetails.userId, user[0].id))
      .limit(1);

    return result[0] ?? null;
  }),

  // Update business plan
  upsert: authenticatedProcedure
    .input(businessPlanSchema)
    .mutation(async ({ ctx, input }) => {
      try {
        // First find the user by clerk_id
        const user = await ctx.db
          .select()
          .from(users)
          .where(eq(users.clerk_id, ctx.auth.userId))
          .limit(1);

        if (!user[0]) {
          throw new Error('User not found');
        }

        // Check if company details already exist for this user
        const existing = await ctx.db
          .select()
          .from(companyDetails)
          .where(eq(companyDetails.userId, user[0].id))
          .limit(1);

        const businessPlanData = {
          businessOverview: input.businessOverview ?? null,
          companyGoals: input.companyGoals ?? null,
          otherBusinessDetails: input.otherBusinessDetails ?? null,
          updatedByUserId: user[0].id,
          updatedAt: new Date(),
        };

        if (existing[0]) {
          // Update existing record - only update business plan fields
          const result = await ctx.db
            .update(companyDetails)
            .set(businessPlanData)
            .where(eq(companyDetails.userId, user[0].id))
            .returning({
              businessOverview: companyDetails.businessOverview,
              companyGoals: companyDetails.companyGoals,
              otherBusinessDetails: companyDetails.otherBusinessDetails,
            });

          return result[0];
        } else {
          // If no company details exist yet, we can't create business plan alone
          // Company details must be created first
          throw new Error(
            'Company details must be created before adding business plan'
          );
        }
      } catch (error) {
        console.error('Failed to upsert business plan:', error);
        throw error;
      }
    }),
});
