import { uuid, timestamp, text } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { basicSchema } from './schemaRoot';

export const users = basicSchema.table('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  clerk_id: text('clerk_id').unique().notNull(),
  email: text('email').unique(),
  first_name: text('first_name'),
  last_name: text('last_name'),
  createdAt: timestamp('created_at', { withTimezone: true })
    .defaultNow()
    .notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date()),
  deletedAt: timestamp('deleted_at', { withTimezone: true }),
});

// Zod schemas generated from Drizzle table
export const insertUserSchema = createInsertSchema(users);
export const selectUserSchema = createSelectSchema(users);

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;

// Note: usersRelations is defined in the main schema file to avoid circular dependencies
