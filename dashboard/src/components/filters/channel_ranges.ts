import { z } from "zod";

// Define the enum values with `as const` for literal type inference
export const channelValues = ['twitter', 'email', 'website', 'all'] as const;

// Type inferred from the values array
export type ChannelValueType = (typeof channelValues)[number];

// Zod enum based on the values array
export const zodChannelEnum = z.enum(channelValues);

// Default channel value
export const DefaultChannelValue: ChannelValueType = 'all';