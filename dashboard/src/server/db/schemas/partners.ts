import { relations } from 'drizzle-orm';
import { text, uuid } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import z from 'zod';
import { createAuditTable } from './helper';
import { users } from './users';

// PARTNERS TABLE SCHEMA
export const partners = createAuditTable('partners', {
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id, {
      onDelete: 'cascade',
      onUpdate: 'cascade',
    }),
  name: text('name').notNull(),
  description: text('description'),
});

// PARTNER FORM SCHEMAS
export const partnerFormSchema = z.object({
  name: z
    .string()
    .min(1, 'Partner name is required')
    .max(100, 'Name must be less than 100 characters'),
  description: z
    .string()
    .max(500, 'Description must be less than 500 characters')
    .optional(),
});

export type PartnerFormData = z.infer<typeof partnerFormSchema>;

// Zod schemas generated from Drizzle table
export const insertPartnerSchema = createInsertSchema(partners);
export const selectPartnerSchema = createSelectSchema(partners);

export type Partner = typeof partners.$inferSelect;
export type NewPartner = typeof partners.$inferInsert;

// RELATIONSHIPS
export const partnersRelations = relations(partners, ({ one }) => ({
  user: one(users, {
    fields: [partners.userId],
    references: [users.id],
  }),
  createdByUser: one(users, {
    fields: [partners.createdByUserId],
    references: [users.id],
  }),
  updatedByUser: one(users, {
    fields: [partners.updatedByUserId],
    references: [users.id],
  }),
}));
