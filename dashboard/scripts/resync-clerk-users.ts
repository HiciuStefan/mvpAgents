// scripts/resync-clerk-users.ts
import 'dotenv/config';
import { upsertClerkUser } from '~/server/db/queries/clerk-webhooks';
import type { UserJSON } from '@clerk/backend';
// We'll create our own connection for this script
import postgres from 'postgres';
import { env } from '~/env.js';

const CLERK_API_KEY = env.CLERK_SECRET_KEY;
const CLERK_API_URL = 'https://api.clerk.dev/v1/users';

async function fetchAllClerkUsers(): Promise<UserJSON[]> {
  if (!CLERK_API_KEY) {
    throw new Error('CLERK_SECRET_KEY environment variable is required');
  }

  let users: UserJSON[] = [];
  const limit = 100;
  let offset = 0;

  console.log('📡 Fetching users from Clerk API...');

  while (true) {
    try {
      const res = await fetch(
        `${CLERK_API_URL}?limit=${limit}&offset=${offset}`,
        {
          headers: {
            Authorization: `Bearer ${CLERK_API_KEY}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!res.ok) {
        throw new Error(`Clerk API error: ${res.status} ${res.statusText}`);
      }

      const data = (await res.json()) as UserJSON[] | { data: UserJSON[] };

      // Clerk API returns users in a 'data' property for paginated responses
      const usersPage = Array.isArray(data) ? data : (data.data ?? []);

      users = users.concat(usersPage);
      console.log(
        `📄 Fetched page with ${usersPage.length} users (offset: ${offset})`
      );

      if (usersPage.length < limit) break; // no more pages
      offset += limit;
    } catch (error) {
      console.error(`❌ Error fetching users at offset ${offset}:`, error);
      throw error;
    }
  }

  return users;
}

async function resyncUsers() {
  try {
    console.log('🔄 Starting user sync from Clerk...');
    const clerkUsers = await fetchAllClerkUsers();
    console.log(`📥 Found ${clerkUsers.length} users in Clerk`);

    let successCount = 0;
    let errorCount = 0;

    for (const user of clerkUsers) {
      try {
        // Pass the entire user object as it matches the UserJSON type
        await upsertClerkUser(user);
        successCount++;
        console.log(
          `✅ Synced user: ${user.id} (${user.email_addresses?.[0]?.email_address ?? 'no email'})`
        );
      } catch (error) {
        errorCount++;
        if (error instanceof Error && error.message.includes('ECONNREFUSED')) {
          console.error(
            `❌ Database connection failed for user ${user.id}. Is PostgreSQL running?`
          );
        } else {
          console.error(`❌ Failed to sync user ${user.id}:`, error);
        }
      }
    }

    console.log(`\n📊 Sync Summary:`);
    console.log(`   ✅ Successfully synced: ${successCount} users`);
    console.log(`   ❌ Failed to sync: ${errorCount} users`);
    console.log(`   📋 Total processed: ${clerkUsers.length} users`);

    if (errorCount > 0 && successCount === 0) {
      console.log(
        `\n💡 Tip: If you're getting database connection errors, make sure:`
      );
      console.log(`   1. PostgreSQL is running (docker-compose up -d)`);
      console.log(`   2. DATABASE_URL is correctly set in your .env file`);
      console.log(`   3. Run: pnpm db:migrate (if needed)`);
    }
  } catch (error) {
    console.error('💥 Fatal error during user sync:', error);
    throw error;
  }
}

// Create a separate connection for this script so we can properly close it
const scriptConn = postgres(env.DATABASE_URL, { prepare: false });

async function main() {
  try {
    await resyncUsers();
    console.log('✅ User sync completed successfully!');
  } catch (error) {
    console.error('💥 Fatal error during user sync:', error);
    process.exit(1);
  } finally {
    try {
      console.log('🧹 Closing DB connection...');
      await scriptConn.end();
      console.log('👋 Script finished. Goodbye!');
      process.exit(0);
    } catch (error) {
      console.error('💥 Fatal error closing DB connection:', error);
      process.exit(1);
    }
  }
}

main().catch(error => {
  console.error('💥 Unhandled error:', error);
  process.exit(1);
});
