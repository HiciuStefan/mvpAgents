import { type Config } from "drizzle-kit";

import { env } from "~/env";
import { TABLE_PREFIX } from "~/server/db/schema";

export default {
  schema: "./src/server/db/schema.ts",
  dialect: "postgresql",
  dbCredentials: {
    url: env.DATABASE_URL,
  },
  tablesFilter: [`${TABLE_PREFIX}_*`],
} satisfies Config;
