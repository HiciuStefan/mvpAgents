import { relations } from 'drizzle-orm';
import { index, text, timestamp, boolean } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { createAgentTable } from './agent-helper';
import { processedItems } from './processed-items';

// Twitter agent table
export const twitter = createAgentTable(
  'twitter',
  {
    tweetId: text('tweet_id').notNull(),
    url: text('url').notNull(),
    text: text('text').notNull(),
  },
  processedItems,
  t => [index('tweet_id_idx').on(t.tweetId)]
);

// Website agent table
export const website = createAgentTable(
  'website',
  {
    url: text('url').notNull(),
    title: text('title').notNull(),
    content: text('content').notNull(),
    opportunityType: text('opportunity_type').notNull(),
    read: boolean('read').notNull().default(false),
    scrapedAt: timestamp('scraped_at', { withTimezone: true }).notNull(),
  },
  processedItems
);

// Email agent table
export const email = createAgentTable(
  'email',
  {
    messageId: text('message_id').notNull(),
    subject: text('subject').notNull(),
    content: text('content').notNull(),
    type: text('type').notNull(), // 'actionable' or 'neutral'
    processedAt: timestamp('processed_at', { withTimezone: true }).notNull(),
  },
  processedItems
);

// Relations
export const twitterRelations = relations(twitter, ({ one }) => ({
  processedItem: one(processedItems, {
    fields: [twitter.processedItemId],
    references: [processedItems.id],
  }),
}));

export const emailRelations = relations(email, ({ one }) => ({
  processedItem: one(processedItems, {
    fields: [email.processedItemId],
    references: [processedItems.id],
  }),
}));

export const websiteRelations = relations(website, ({ one }) => ({
  processedItem: one(processedItems, {
    fields: [website.processedItemId],
    references: [processedItems.id],
  }),
}));

// Zod schemas generated from Drizzle tables
export const insertTwitterSchema = createInsertSchema(twitter);
export const selectTwitterSchema = createSelectSchema(twitter);
export const insertWebsiteSchema = createInsertSchema(website);
export const selectWebsiteSchema = createSelectSchema(website);
export const insertEmailSchema = createInsertSchema(email);
export const selectEmailSchema = createSelectSchema(email);

// Types
export type Twitter = typeof twitter.$inferSelect;
export type NewTwitter = typeof twitter.$inferInsert;
export type Website = typeof website.$inferSelect;
export type NewWebsite = typeof website.$inferInsert;
export type Email = typeof email.$inferSelect;
export type NewEmail = typeof email.$inferInsert;
