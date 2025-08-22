import z from 'zod';

// Re-export everything from the organized schema modules
export * from './schemas';

// Re-export utilities for backward compatibility
export { TABLE_PREFIX, createTable } from './utils';

// GET schema for GET requests
export const processed_GET_schema = z.object({
  limit: z.coerce.number().int().positive().default(1),
  client_name: z.string().min(1).optional(),
});

export const processed_DELETE_schema = z.object({
  client_name: z.string().min(1).optional(),
});

export const processed_DELETE_by_id_schema = z.object({
  id: z.string(),
});

// NEW SCHEMAS FOR RAG
// POST schema for POST requests
export const rag_post_schema = z.object({
  input: z.string(),
});

// GET schema for GET requests
export const rag_get_schema = z.object({
  text: z.string(),
});

// DELETE schema for DELETE requests
export const rag_delete_schema = z.object({
  confirm: z.boolean().optional(), // Optional confirmation flag
});
