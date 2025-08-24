import { uuid, timestamp, text, index } from 'drizzle-orm/pg-core';
import type {
  IndexBuilder,
  PgColumnBuilderBase,
  AnyPgColumn,
} from 'drizzle-orm/pg-core';
import { users } from './users';
import { basicSchema } from './schemaRoot';

export interface BaseColumns {
  id: PgColumnBuilderBase;
  createdAt: PgColumnBuilderBase;
  updatedAt: PgColumnBuilderBase;
  createdByUserId: PgColumnBuilderBase;
  updatedByUserId: PgColumnBuilderBase;
  deletedAt: PgColumnBuilderBase;
}

// Define the table column type for the index callback
export type TableColumns<T extends Record<string, PgColumnBuilderBase>> = {
  [K in keyof T]: AnyPgColumn;
};

export function createAuditTable<T extends Record<string, PgColumnBuilderBase>>(
  name: string,
  extraColumns: T,
  indexes?: (table: TableColumns<BaseColumns & T>) => IndexBuilder[]
) {
  const baseColumns = {
    id: uuid('id').primaryKey().defaultRandom(),
    createdAt: timestamp('created_at', { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: updatedAtColumn(),
    createdByUserId: uuid('created_by_user_id').references(() => users.id),
    updatedByUserId: uuid('updated_by_user_id').references(() => users.id),
    deletedAt: timestamp('deleted_at', { withTimezone: true }),
  };

  const allColumns = {
    ...baseColumns,
    ...extraColumns,
  } as const;

  return basicSchema.table(name, allColumns, table => {
    const defaultIndexes = [
      index(`${name}_created_at_idx`).on(table.createdAt),
    ];
    // Custom indexes from the provided callback
    const customIndexes = indexes
      ? indexes(table as TableColumns<BaseColumns & T>)
      : [];

    return [...defaultIndexes, ...customIndexes];
  });
}

/** Helper for reusable updatedAt column */
function updatedAtColumn(name = 'updated_at') {
  return timestamp(name, { withTimezone: true })
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date());
}
