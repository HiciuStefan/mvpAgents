import z from 'zod';

// BUSINESS PLAN FORM SCHEMA
export const businessPlanSchema = z.object({
  businessOverview: z
    .string()
    .max(2000, 'Business overview must be less than 2000 characters')
    .optional()
    .or(z.literal('')),
  companyGoals: z
    .string()
    .max(2000, 'Company goals must be less than 2000 characters')
    .optional()
    .or(z.literal('')),
  otherBusinessDetails: z
    .string()
    .max(2000, 'Other business details must be less than 2000 characters')
    .optional()
    .or(z.literal('')),
});

export type BusinessPlanData = z.infer<typeof businessPlanSchema>;
