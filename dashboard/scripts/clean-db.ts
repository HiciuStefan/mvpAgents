import postgres from 'postgres';
// import dotenv from 'dotenv';

// dotenv.config();

const main = async (): Promise<void> => {
  if (!process.env.POSTGRES_URL) {
    throw new Error('POSTGRES_URL environment variable is required');
  }

  const connection = postgres(process.env.POSTGRES_URL, {
    connection: {
      search_path: 'graphium',
    },
  });

  try {
    console.log(`🗑️  Dropping schema "drizzle" if it exists...`);
    await connection`DROP SCHEMA IF EXISTS drizzle CASCADE`;

    console.log(`🗑️  Dropping schema "graphium" if it exists...`);
    await connection`DROP SCHEMA IF EXISTS graphium CASCADE`;

    console.log(`✅ Schema "graphium" cleaned successfully!`);
    console.log(`💡 Next steps:`);
    console.log(`   1. Run: pnpm db:migrate`);
    console.log(`   2. Run: pnpm db:seed:dev`);
  } catch (error) {
    console.error('❌ Error cleaning database schema:', error);
    process.exit(1);
  } finally {
    await connection.end();
  }
};

main().catch(error => {
  console.error('❌ Unexpected error:', error);
  process.exit(1);
});
