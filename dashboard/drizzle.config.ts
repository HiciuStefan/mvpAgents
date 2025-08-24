// import 'dotenv/config';
import { type Config } from 'drizzle-kit';
import { env } from '~/env';
import { schemaName } from './src/server/db/schemas/schemaRoot';

export default {
  schema: './src/server/db/schema.ts',
  out: './src/server/db/migrations',
  dialect: 'postgresql',
  schemaFilter: [schemaName],
  dbCredentials: {
    url: env.DATABASE_URL,
  },
  verbose: true,
  strict: true,
} satisfies Config;
