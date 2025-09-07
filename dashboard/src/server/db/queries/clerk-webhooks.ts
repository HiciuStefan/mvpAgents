import { eq, and } from 'drizzle-orm';
import { db } from '../index';
import type {
  UserJSON,
  OrganizationJSON,
  DeletedObjectJSON,
  OrganizationMembershipJSON,
} from '@clerk/backend';
import { users, users_organizations } from '~/server/db/schemas/users';
import { organizations } from '~/server/db/schemas/users';

export async function upsertClerkUser(data: UserJSON): Promise<void> {
  const {
    id: userId,
    first_name: firstName,
    last_name: lastName,
    email_addresses: emailAddresses,
    primary_email_address_id: primaryEmailAddressId,
    created_at: createdAt,
    updated_at: updatedAt,
  } = data;

  // Get primary email
  const primaryEmail = emailAddresses.find(
    email => email.id === primaryEmailAddressId
  );
  if (!primaryEmail) {
    throw new Error('No primary email found for user');
  }

  await db
    .insert(users)
    .values({
      clerk_id: userId,
      firstName: firstName ?? '',
      lastName: lastName ?? '',
      email: primaryEmail.email_address,
      isActive: true,
      createdAt: new Date(createdAt),
      updatedAt: new Date(updatedAt),
      webhook: true,
    })
    .onConflictDoUpdate({
      target: users.clerk_id,
      set: {
        firstName: firstName ?? '',
        lastName: lastName ?? '',
        email: primaryEmail.email_address,
        updatedAt: new Date(updatedAt),
        webhook: true,
      },
    });

  console.log('User upserted successfully:', userId);
}

export async function deleteClerkUser(data: DeletedObjectJSON): Promise<void> {
  const { id: userId } = data;

  if (!userId) {
    throw new Error('No user ID provided');
  }
  await db
    .update(users)
    .set({ isActive: false, updatedAt: new Date() })
    .where(eq(users.clerk_id, userId));

  console.log('User deactivated successfully:', userId);
}

export async function upsertClerkOrganization(
  data: OrganizationJSON
): Promise<void> {
  const {
    id: clerkOrganizationId,
    name,
    created_by: createdBy,
    created_at: createdAt,
    updated_at: updatedAt,
  } = data;

  if (!createdBy) {
    throw new Error('No creator ID provided');
  }

  // Find creator user
  const creatorUser = await db.query.users.findFirst({
    where: eq(users.clerk_id, createdBy),
  });

  if (!creatorUser) {
    throw new Error('Creator user not found');
  }

  // Upsert organization (insert or update)
  await db
    .insert(organizations)
    .values({
      name: name,
      organizationId: clerkOrganizationId,
      createdAt: new Date(createdAt),
      updatedAt: new Date(updatedAt),
    })
    .onConflictDoUpdate({
      target: organizations.organizationId,
      set: {
        name: name,
        updatedAt: new Date(updatedAt),
      },
    });

  console.log('Organization upserted successfully:', clerkOrganizationId);
}

export async function deleteClerkOrganization(
  data: DeletedObjectJSON
): Promise<void> {
  const { id: clerkOrganizationId } = data;

  if (!clerkOrganizationId) {
    throw new Error('No organization ID provided');
  }

  await db
    .delete(organizations)
    .where(eq(organizations.organizationId, clerkOrganizationId));

  console.log('Organization deleted successfully:', clerkOrganizationId);
}

export async function upsertClerkOrganizationMembership(
  data: OrganizationMembershipJSON
): Promise<void> {
  const { public_user_data: userData, organization: orgData } = data;

  if (!userData?.user_id || !orgData?.id) {
    throw new Error('Missing required user or organization data');
  }

  // Verify the user exists in our database
  const existingUserPromise = db.query.users.findFirst({
    where: eq(users.clerk_id, userData.user_id),
  });

  const existingOrgPromise = db.query.organizations.findFirst({
    where: eq(organizations.organizationId, orgData.id),
  });

  const [existingUser, existingOrg] = await Promise.all([
    existingUserPromise,
    existingOrgPromise,
  ]);

  if (!existingUser || !existingOrg) {
    throw new Error(
      `User/org ${userData.user_id} or ${orgData.id} not found in database`
    );
  }

  // Create the membership relationship
  await db
    .insert(users_organizations)
    .values({
      userId: userData.user_id,
      organizationId: orgData.id,
    })
    .onConflictDoNothing(); // Don't update if already exists

  console.log(
    `Successfully synced organization membership: ${userData.user_id} -> ${orgData.id}`
  );
}

export async function deleteClerkOrganizationMembership(
  data: OrganizationMembershipJSON
): Promise<void> {
  const deletedRows = await db
    .delete(users_organizations)
    .where(
      and(
        eq(users_organizations.userId, data.public_user_data.user_id),
        eq(users_organizations.organizationId, data.organization.id)
      )
    );

  console.log(
    `Deleted organization membership with ID: ${data.id}. Deleted ${deletedRows.length} rows.`
  );
}
