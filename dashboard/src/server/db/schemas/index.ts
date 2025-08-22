// Export all schema components for easy importing

// Tables
export * from './users';
export * from './partners';
export * from './processed-items';
export * from './agent-tables';

// Validation schemas
export * from './validation-schemas';

// Utilities
export * from './helper';
export * from './agent-helper';
export * from './schemaRoot';

// Re-export relations that need to be defined here to avoid circular dependencies
import { relations } from 'drizzle-orm';
import { processedItems } from './processed-items';
import { twitter, email, website } from './agent-tables';

// Main processed items relations
export const processedItemsRelations = relations(processedItems, ({ one }) => ({
  twitter: one(twitter, {
    fields: [processedItems.id],
    references: [twitter.processedItemId],
  }),
  email: one(email, {
    fields: [processedItems.id],
    references: [email.processedItemId],
  }),
  website: one(website, {
    fields: [processedItems.id],
    references: [website.processedItemId],
  }),
}));
