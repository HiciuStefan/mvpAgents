#!/usr/bin/env tsx

import postgres from 'postgres';
// import dotenv from 'dotenv';
import path from 'path';

// Store original value before loading .env
const originalPostgresUrl = process.env.POSTGRES_URL;

// Load .env from project root, not scripts directory (override existing env vars)
// dotenv.config({ path: path.join(__dirname, '..', '.env'), override: true });

console.log('POSTGRES_URL before loading .env:', originalPostgresUrl);
console.log('POSTGRES_URL after loading .env:', process.env.POSTGRES_URL);
console.log(
  'All postgres-related env vars:',
  Object.keys(process.env).filter(key => key.includes('POSTGRES'))
);

if (!process.env.POSTGRES_URL) {
  console.error('❌ POSTGRES_URL environment variable is not set!');
  console.log('Current working directory:', process.cwd());

  console.log(
    'Available env files:',
    // eslint-disable-next-line @typescript-eslint/no-require-imports, @typescript-eslint/no-unsafe-call
    require('fs')
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      .readdirSync('.')
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      .filter((f: string) => f.startsWith('.env'))
  );
  console.log('Expected connection string: postgresql://postgres:postgres@localhost:5432/dev_db');
  process.exit(1);
}

async function testConnection(): Promise<boolean> {
  console.log('Testing database connection...');
  try {
    const sql = postgres(process.env.POSTGRES_URL!, {
      connect_timeout: 5,
      idle_timeout: 1,
      max_lifetime: 1,
    });

    await sql`SELECT 1`;
    await sql.end();
    console.log('\x1b[32m%s\x1b[0m', 'Database connection test successful');
    return true;
  } catch (error) {
    console.error('Database connection failed:', error);
    return false;
  }
}

// If called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testConnection()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(() => {
      process.exit(1);
    });
}

export { testConnection };
