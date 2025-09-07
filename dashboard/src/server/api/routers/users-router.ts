import { createTRPCRouter, authenticatedProcedure } from '~/server/api/trpc';
import { users_organizations } from '~/server/db/schemas/users';
import { db } from '~/server/db';
import { eq } from 'drizzle-orm';
import type { User } from '~/server/db/types/users';

export const usersRouter = createTRPCRouter({
  getAll: authenticatedProcedure.query(async ({ ctx }): Promise<User[]> => {
    const { user } = ctx;

    const usersList = await db.query.users.findMany({
      with: {
        usersOrganizations: {
          where: eq(users_organizations.organizationId, user.orgId),
        },
      },
    });

    return usersList;
  }),
});
