import { pgSchema } from 'drizzle-orm/pg-core';

export const schemaName = 'agents';

export const basicSchema = pgSchema(schemaName);
