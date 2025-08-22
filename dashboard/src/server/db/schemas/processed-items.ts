import { pgEnum, boolean, integer, text } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { createAuditTable } from './helper';

// Enum for processed item types
export const processedItemTypeEnum = pgEnum('item_type', [
  'email',
  'twitter',
  'website',
]);

export type ProcessedItemType =
  (typeof processedItemTypeEnum.enumValues)[number];

// Main processed items table
export const processedItems = createAuditTable('processed_items', {
  type: processedItemTypeEnum().notNull(),
  actionable: boolean('actionable').notNull().default(false),
  urgency: integer('urgency').notNull().default(0),
  clientName: text('client_name').notNull(),
});

// Zod schemas generated from Drizzle table
export const insertProcessedItemSchema = createInsertSchema(processedItems);
export const selectProcessedItemSchema = createSelectSchema(processedItems);

// Relations - imported dynamically to avoid circular dependencies
// These will be defined in the main schema file that imports all tables

export type ProcessedItem = typeof processedItems.$inferSelect;
export type NewProcessedItem = typeof processedItems.$inferInsert;
