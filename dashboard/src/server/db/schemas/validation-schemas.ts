import z from 'zod';

// Note: Drizzle-zod schemas are generated in individual table files
// This file contains custom validation schemas for API endpoints

// Base schema for all agent input objects
export const baseAgentInputSchema = z.object({
  client_name: z.string().min(1, 'Client name is required'),
  short_description: z.string(),
  relevance: z.string(),
  actionable: z.boolean(),
  suggested_action: z.string(),
  suggested_reply: z.string(),
  urgency: z.number().int().min(0).max(3).default(0),
});

// Twitter validation schema
export const processedTweetsSchema = baseAgentInputSchema.extend({
  tweet_id: z.string().min(1, 'Tweet ID is required'),
  url: z.string().url('Must be a valid URL'),
  text: z.string().min(1, 'Text is required'),
});

// Website validation schema
export const processedWebsitesSchema = baseAgentInputSchema.extend({
  url: z.string().url('Must be a valid URL'),
  title: z.string().min(1, 'Title is required'),
  content: z.string().min(1, 'Content is required'),
  opportunity_type: z.string().min(1, 'Opportunity type is required'),
  read: z.boolean(),
  scraped_at: z
    .union([z.string().transform(val => new Date(val)), z.date()])
    .refine(date => !isNaN(date.getTime()), {
      message: 'Invalid date format',
    }),
});

// Email validation schema
export const processedEmailsSchema = baseAgentInputSchema.extend({
  message_id: z.string().min(1),
  subject: z.string().min(1),
  content: z.string().min(1),
  type: z.string().min(1),
  processed_at: z
    .union([z.string().transform(val => new Date(val)), z.date()])
    .refine(date => !isNaN(date.getTime()), {
      message: 'Invalid date format',
    }),
});

// GET schema for GET requests
export const processedGetSchema = z.object({
  type: z.enum(['email', 'twitter', 'website']).optional(),
  actionable: z.boolean().optional(),
  urgency: z.number().int().min(0).max(3).optional(),
  limit: z.number().int().min(1).max(100).default(10),
  offset: z.number().int().min(0).default(0),
});

// POST schema for creating processed items
export const processedPostSchema = z.object({
  type: z.enum(['email', 'twitter', 'website']),
  actionable: z.boolean().default(false),
  urgency: z.number().int().min(0).max(3).default(0),
  client_name: z.string().min(1, 'Client name is required'),
  // Additional fields based on type will be validated separately
});

// API-specific validation schemas
// These are used for validating API requests and responses

// Export types
export type BaseAgentInput = z.infer<typeof baseAgentInputSchema>;
export type ProcessedTweet = z.infer<typeof processedTweetsSchema>;
export type ProcessedWebsite = z.infer<typeof processedWebsitesSchema>;
export type ProcessedEmail = z.infer<typeof processedEmailsSchema>;
export type ProcessedGetRequest = z.infer<typeof processedGetSchema>;
export type ProcessedPostRequest = z.infer<typeof processedPostSchema>;

// Note: For database insert/select validation, use the drizzle-zod generated schemas
// from individual table files (insertUserSchema, selectUserSchema, etc.)
