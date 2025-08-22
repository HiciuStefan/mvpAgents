import { pgTableCreator } from 'drizzle-orm/pg-core';

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

