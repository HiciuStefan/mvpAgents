import type { InferSelectModel } from 'drizzle-orm';
import type { users, organizations } from '~/server/db/schemas/users';

export type User = InferSelectModel<typeof users>;
export type Organization = InferSelectModel<typeof organizations>;
