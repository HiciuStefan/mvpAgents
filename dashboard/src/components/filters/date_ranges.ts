import { z } from "zod";

// Define the enum values with `as const` for literal type inference
export const dateRangeValues = ['today', 'last_week', 'last_30_days'] as const;

// Type inferred from the values array
export type DateRangeValueType = (typeof dateRangeValues)[number];

// Zod enum based on the values array
export const zodDateRangeEnum = z.enum(dateRangeValues);

// Default date range value
export const DefaultDateRangeValue: DateRangeValueType = 'last_week';