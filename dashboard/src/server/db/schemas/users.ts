import { uuid, timestamp, text, boolean } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { basicSchema } from './schemaRoot';
import { updatedAtColumn } from './helper';

export const users = basicSchema.table('users', {
  id: uuid('id').unique().primaryKey().defaultRandom(),
  clerk_id: text('clerk_id').unique().notNull(),
  email: text('email').unique(),
  isActive: boolean('is_active').default(true),
  firstName: text('first_name').notNull(),
  lastName: text('last_name').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true })
    .defaultNow()
    .notNull(),
  updatedAt: updatedAtColumn('updated_at'),
  deletedAt: timestamp('deleted_at', { withTimezone: true }),
  webhook: boolean('webhook').default(false),
});

// Zod schemas generated from Drizzle table
export const insertUserSchema = createInsertSchema(users);
export const selectUserSchema = createSelectSchema(users);

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;

// Note: usersRelations is defined in the main schema file to avoid circular dependencies

export const organizations = basicSchema.table('organizations', {
  organizationId: text('organization_id').unique().primaryKey(),
  name: text('name').notNull(),
  createdBy: uuid(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt: updatedAtColumn('updated_at'),
  deletedAt: timestamp('deleted_at', { withTimezone: true }),
});

export const users_organizations = basicSchema.table('users_organizations', {
  userId: text('user_id')
    .references(() => users.id)
    .notNull(),
  organizationId: text('organization_id')
    .references(() => organizations.organizationId)
    .notNull(),
});

// Relationships
export const usersRelations = relations(users, ({ many }) => ({
  // A user can belong to many organizations through the junction table
  usersOrganizations: many(users_organizations),
}));

// Relationships
export const organizationsRelations = relations(organizations, ({ many }) => ({
  // An organization can have many users through the junction table
  usersOrganizations: many(users_organizations),
}));

export const usersOrganizationsRelations = relations(
  users_organizations,
  ({ one }) => ({
    user: one(users, {
      fields: [users_organizations.userId],
      references: [users.id],
    }),
    organization: one(organizations, {
      fields: [users_organizations.organizationId],
      references: [organizations.organizationId],
    }),
  })
);
