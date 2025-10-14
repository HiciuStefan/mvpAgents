import { createTRPCRouter, authenticatedProcedure } from '~/server/api/trpc';
import { companyDetailsFormSchema } from '~/server/db/schemas/company-details';
import { companyDetails } from '~/server/db/schemas/company-details';
import { users } from '~/server/db/schemas/users';
import { eq } from 'drizzle-orm';

export const companyDetailsRouter = createTRPCRouter({
  // Get company details for the current user
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

    // Then get company details using the user's UUID
    const result = await ctx.db
      .select()
      .from(companyDetails)
      .where(eq(companyDetails.userId, user[0].id))
      .limit(1);

    return result[0] ?? null;
  }),

  // Create or update company details
  upsert: authenticatedProcedure
    .input(companyDetailsFormSchema)
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

        const companyData = {
          userId: user[0].id,
          companyName: input.companyName,
          industry: input.industry,
          companyDescription: input.companyDescription,
          website: input.website ?? null,
          createdByUserId: user[0].id,
          updatedByUserId: user[0].id,
        };

        if (existing[0]) {
          // Update existing record
          const result = await ctx.db
            .update(companyDetails)
            .set({
              ...companyData,
              updatedAt: new Date(),
            })
            .where(eq(companyDetails.userId, user[0].id))
            .returning();

          return result[0];
        } else {
          // Create new record
          const result = await ctx.db
            .insert(companyDetails)
            .values(companyData)
            .returning();

          return result[0];
        }
      } catch (error) {
        console.error('Failed to upsert company details:', error);
        throw new Error('Failed to upsert company details');
      }
    }),

  // Delete company details
  delete: authenticatedProcedure.mutation(async ({ ctx }) => {
    // First find the user by clerk_id
    const user = await ctx.db
      .select()
      .from(users)
      .where(eq(users.clerk_id, ctx.auth.userId))
      .limit(1);

    if (!user[0]) {
      throw new Error('User not found');
    }

    const result = await ctx.db
      .delete(companyDetails)
      .where(eq(companyDetails.userId, user[0].id))
      .returning();

    return result[0];
  }),
});
