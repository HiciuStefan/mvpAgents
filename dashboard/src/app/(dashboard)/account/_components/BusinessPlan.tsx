'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '~/components/ui/button';
import { Textarea } from '~/components/ui/textarea';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card';
import { FileText, Save } from 'lucide-react';
import { api } from '~/trpc/react';

import {
  businessPlanSchema,
  type BusinessPlanData,
} from '~/server/db/schemas/business-plan';

export function BusinessPlan() {
  const { data: businessPlan, isLoading } = api.businessPlan.get.useQuery();
  const upsertMutation = api.businessPlan.upsert.useMutation();

  const form = useForm<BusinessPlanData>({
    resolver: zodResolver(businessPlanSchema),
    defaultValues: {
      businessOverview: businessPlan?.businessOverview ?? '',
      companyGoals: businessPlan?.companyGoals ?? '',
      otherBusinessDetails: businessPlan?.otherBusinessDetails ?? '',
    },
  });

  // Update form values when data loads
  useEffect(() => {
    if (businessPlan) {
      form.reset({
        businessOverview: businessPlan.businessOverview ?? '',
        companyGoals: businessPlan.companyGoals ?? '',
        otherBusinessDetails: businessPlan.otherBusinessDetails ?? '',
      });
    }
  }, [businessPlan, form]);

  const onSubmit = async (data: BusinessPlanData) => {
    try {
      await upsertMutation.mutateAsync(data);
      // TODO: Show success message
    } catch (error) {
      console.error('Failed to save business plan:', error);
      // TODO: Show error message
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Business Plan</span>
          </CardTitle>
          <CardDescription>
            Define your business strategy, goals, and execution plan.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
            </div>
          ) : (
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <label
                  htmlFor="businessOverview"
                  className="block text-sm font-medium mb-2"
                >
                  Business Overview
                </label>
                <Textarea
                  id="businessOverview"
                  {...form.register('businessOverview')}
                  placeholder="Describe your company's business plan and strategy. Include your business model, target market, competitive advantages, and overall approach..."
                  rows={6}
                  className={
                    form.formState.errors.businessOverview
                      ? 'border-red-500'
                      : ''
                  }
                />
                {form.formState.errors.businessOverview && (
                  <p className="text-red-500 text-sm mt-1">
                    {form.formState.errors.businessOverview.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="companyGoals"
                  className="block text-sm font-medium mb-2"
                >
                  Company Goals
                </label>
                <Textarea
                  id="companyGoals"
                  {...form.register('companyGoals')}
                  placeholder="Define your specific company-wide goals. For example: 'vreau 5 clienti pe twitter', 'vreau pe partenerii mei sa vand mai mult', 'discounturi mai mici'..."
                  rows={6}
                  className={
                    form.formState.errors.companyGoals ? 'border-red-500' : ''
                  }
                />
                {form.formState.errors.companyGoals && (
                  <p className="text-red-500 text-sm mt-1">
                    {form.formState.errors.companyGoals.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="otherBusinessDetails"
                  className="block text-sm font-medium mb-2"
                >
                  Other Business Details
                </label>
                <Textarea
                  id="otherBusinessDetails"
                  {...form.register('otherBusinessDetails')}
                  placeholder="Add any other important business details, operational notes, or strategic information..."
                  rows={6}
                  className={
                    form.formState.errors.otherBusinessDetails
                      ? 'border-red-500'
                      : ''
                  }
                />
                {form.formState.errors.otherBusinessDetails && (
                  <p className="text-red-500 text-sm mt-1">
                    {form.formState.errors.otherBusinessDetails.message}
                  </p>
                )}
              </div>

              <div className="flex justify-end">
                <Button type="submit" disabled={upsertMutation.isPending}>
                  <Save className="h-4 w-4 mr-2" />
                  {upsertMutation.isPending
                    ? 'Saving...'
                    : 'Save Business Plan'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
