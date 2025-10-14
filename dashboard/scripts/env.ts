// scripts/env.ts - Script-specific environment configuration
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const scriptEnv = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    CLERK_SECRET_KEY: z.string(),
  },
  client: {},
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY,
  },
  skipValidation: false,
  emptyStringAsUndefined: true,
});
