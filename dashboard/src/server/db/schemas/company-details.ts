import { relations } from 'drizzle-orm';
import { text, uuid } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import z from 'zod';
import { createAuditTable } from './helper';
import { users } from './users';

// COMPANY DETAILS TABLE SCHEMA
export const companyDetails = createAuditTable('company_details', {
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id, {
      onDelete: 'cascade',
      onUpdate: 'cascade',
    }),
  companyName: text('company_name').notNull(),
  industry: text('industry').notNull(),
  companyDescription: text('company_description').notNull(),
  website: text('website'),
  businessOverview: text('business_overview'),
  companyGoals: text('company_goals'),
  otherBusinessDetails: text('other_business_details'),
});

// COMPANY DETAILS FORM SCHEMAS
export const companyDetailsFormSchema = z.object({
  companyName: z
    .string()
    .min(1, 'Company name is required')
    .max(100, 'Company name must be less than 100 characters'),
  industry: z
    .string()
    .min(1, 'Industry is required')
    .max(100, 'Industry must be less than 100 characters'),
  companyDescription: z
    .string()
    .min(1, 'Company description is required')
    .max(1000, 'Company description must be less than 1000 characters'),
  website: z
    .string()
    .url('Please enter a valid URL')
    .optional()
    .or(z.literal('')),
});

export type CompanyDetailsFormData = z.infer<typeof companyDetailsFormSchema>;

// Zod schemas generated from Drizzle table
export const insertCompanyDetailsSchema = createInsertSchema(companyDetails);
export const selectCompanyDetailsSchema = createSelectSchema(companyDetails);

export type CompanyDetails = typeof companyDetails.$inferSelect;
export type NewCompanyDetails = typeof companyDetails.$inferInsert;

// RELATIONSHIPS
export const companyDetailsRelations = relations(companyDetails, ({ one }) => ({
  user: one(users, {
    fields: [companyDetails.userId],
    references: [users.id],
  }),
  createdByUser: one(users, {
    fields: [companyDetails.createdByUserId],
    references: [users.id],
  }),
  updatedByUser: one(users, {
    fields: [companyDetails.updatedByUserId],
    references: [users.id],
  }),
}));
