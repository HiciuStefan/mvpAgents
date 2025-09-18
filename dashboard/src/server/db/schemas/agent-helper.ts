import { text, uuid } from 'drizzle-orm/pg-core';
import type {
  AnyPgTable,
  PgColumnBuilderBase,
  IndexBuilder,
  AnyPgColumn,
} from 'drizzle-orm/pg-core';
import { createAuditTable } from './helper';
import type { BaseColumns, TableColumns } from './helper';

// Define agent-specific columns interface for type safety
interface AgentColumns {
  processedItemId: PgColumnBuilderBase;
  shortDescription: PgColumnBuilderBase;
  relevance: PgColumnBuilderBase;
  suggestedAction: PgColumnBuilderBase;
  suggestedReply: PgColumnBuilderBase;
}

// Function to create agent-specific audit tables with shared agent fields
// This helper includes all common fields that agent tables need
export function createAgentTable<
  T extends Record<string, PgColumnBuilderBase>,
  P extends AnyPgTable & { id: AnyPgColumn },
>(
  name: string,
  extraColumns: T,
  processedItemsTable: P,
  indexes?: (
    table: TableColumns<BaseColumns & T & AgentColumns>
  ) => IndexBuilder[]
) {
  const agentColumns = {
    processedItemId: uuid('processed_item_id')
      .notNull()
      .references(() => processedItemsTable.id, {
        onDelete: 'cascade',
        onUpdate: 'cascade',
      }),
    shortDescription: text('short_description').notNull(),
    relevance: text('relevance'),
    suggestedAction: text('suggested_action'),
    suggestedReply: text('suggested_reply').notNull().default(''),
  };

  // Combine agent columns with extra columns
  const allColumns = {
    ...agentColumns,
    ...extraColumns,
  } as const;

  // Pass to createAuditTable with combined columns and indexes
  return createAuditTable(name, allColumns, indexes);
}
