// Example model schema from the Drizzle docs
// https://orm.drizzle.team/docs/sql-schema-declaration
import z from 'zod';
import { sql } from 'drizzle-orm';
import { relations } from 'drizzle-orm';
import { pgEnum, pgTableCreator } from 'drizzle-orm/pg-core';
import type { PgColumnBuilderBase } from 'drizzle-orm/pg-core';

/**
 * Single source of truth for table prefix
 * Change this to update the prefix across the entire application
 */
export const TABLE_PREFIX = 'deai';

/**
 * This is an example of how to use the multi-project schema feature of Drizzle ORM. Use the same
 * database instance for multiple projects.
 *
 * @see https://orm.drizzle.team/docs/goodies#multi-project-schema
 */
export const createTable = pgTableCreator((name) => `${TABLE_PREFIX}_${name}`);


export function create_agent_table<
  T extends Record<string, PgColumnBuilderBase>
>(
  name: string,
  extraColumns: (d: Parameters<Parameters<typeof createTable>[1]>[0]) => T
) {
	return createTable(name, (d) => ({
		id: d.uuid().primaryKey().defaultRandom(),
		processed_item_id: d.uuid().notNull().references(() => processed_items.id, {
			onDelete: 'cascade',
			onUpdate: 'cascade'
		}),
		short_description: d.text().notNull(),
		relevance: d.text(),
		suggested_action: d.text(),
		...extraColumns(d),
	}));
}

export const processedItemTypeEnum  = pgEnum("item_type", ["email", "twitter", "website"]);

export type ProcessedItemType = (typeof processedItemTypeEnum.enumValues)[number];

// Base schema for all agent input objects
export const baseAgentInputSchema = z.object({
	client_name: z.string().min(1, 'Client name is required'),
	short_description: z.string(),
	relevance: z.string(),
	actionable: z.boolean(),
	suggested_action: z.string(),
});

// Main processed items table
export const processed_items = createTable('processed_items',
	(d) => ({
		id: d.uuid().primaryKey().defaultRandom(),
		type: processedItemTypeEnum().notNull(),
		actionable: d.boolean().notNull().default(false),
		client_name: d.text().notNull(),
		created_at: d
		.timestamp({ withTimezone: true })
		.default(sql`CURRENT_TIMESTAMP`)
		.notNull(),
		updated_at: d.timestamp({ withTimezone: true }).$onUpdate(() => new Date()),
	})
);

// INPUT OBJECT - TWEETS
export const processed_tweets_schema = baseAgentInputSchema.extend({
	tweet_id: z.string().min(1, 'Tweet ID is required'),
	url: z.string().url('Must be a valid URL'),
	text: z.string().min(1, 'Text is required'),
	status: z.string().min(1, 'Status is required'),
	reply: z.string(),
});

export const twitter = create_agent_table('twitter',
	(d) => ({
		tweet_id: d.text().notNull(),
		url: d.text().notNull(),
		text: d.text().notNull(),
		status: d.text().notNull(), // 'pending', 'posted', or 'rejected'
		reply: d.text().notNull().default(''),
	}),
	// (t) => [index('name_idx').on(t.name)]
);


// INPUT OBJECT - WEBSITE
export const processed_websites_schema = baseAgentInputSchema.extend({
	url: z.string().url('Must be a valid URL'),
	title: z.string().min(1, 'Title is required'),
	content: z.string().min(1, 'Content is required'),
	opportunity_type: z.string().min(1, 'Opportunity type is required'),
	read: z.boolean(),
	scraped_at: z.union([
		z.string().transform((val) => new Date(val)),
		z.date()
	]).refine((date) => !isNaN(date.getTime()), {
		message: 'Invalid date format',
	}),
});


export const website = create_agent_table('website',
	(d) => ({
		url: d.text().notNull(),
		title: d.text().notNull(),
		content: d.text().notNull(),
		opportunity_type: d.text().notNull(),
		read: d.boolean().notNull().default(false),
		scraped_at: d.timestamp({ withTimezone: true }).notNull()
	})
);


// INPUT OBJECT - EMAIL
export const processed_emails_schema = baseAgentInputSchema.extend({
	message_id: z.string().min(1),
	subject: z.string().min(1),
	content: z.string().min(1),
	type: z.string().min(1),
	processed_at: z.union([
		z.string().transform((val) => new Date(val)),
		z.date()
	]).refine((date) => !isNaN(date.getTime()), {
		message: 'Invalid date format',
	}),
});



export const email = create_agent_table('email',
	(d) => ({
		message_id: d.text().notNull(),
		subject: d.text().notNull(),
		content: d.text().notNull(),
		type: d.text().notNull(), // 'actionable' or 'neutral',
		processed_at: d.timestamp({ withTimezone: true }).notNull(),
	})
);

// Define relationships
export const processedItemsRelations = relations(processed_items, ({ one }) => ({
	twitter: one(twitter, {
		fields: [processed_items.id],
		references: [twitter.processed_item_id],
	}),
	email: one(email, {
		fields: [processed_items.id],
		references: [email.processed_item_id],
	}),
	website: one(website, {
		fields: [processed_items.id],
		references: [website.processed_item_id],
	}),
}));

export const twitterRelations = relations(twitter, ({ one }) => ({
	processed_item: one(processed_items, {
		fields: [twitter.processed_item_id],
		references: [processed_items.id],
	}),
}));

export const emailRelations = relations(email, ({ one }) => ({
	processed_item: one(processed_items, {
		fields: [email.processed_item_id],
		references: [processed_items.id],
	}),
}));

export const websiteRelations = relations(website, ({ one }) => ({
	processed_item: one(processed_items, {
		fields: [website.processed_item_id],
		references: [processed_items.id],
	}),
}));



// GET schema for GET requests
export const processed_GET_schema = z.object({
	limit: z.coerce.number().int().positive().default(1),
	client_name: z.string().min(1).optional()
});

export const processed_DELETE_schema = z.object({
	client_name: z.string().min(1).optional()
});

export const processed_DELETE_by_id_schema = z.object({
	id: z.string()
});

// NEW SCHEMAS FOR RAG
// POST schema for POST requests
export const rag_post_schema = z.object({
	input: z.string()
});

// GET schema for GET requests
export const rag_get_schema = z.object({
	text: z.string()
});

// DELETE schema for DELETE requests
export const rag_delete_schema = z.object({
	confirm: z.boolean().optional() // Optional confirmation flag
});