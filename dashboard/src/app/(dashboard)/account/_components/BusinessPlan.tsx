'use client'

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '~/components/ui/button';
import { Textarea } from '~/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { FileText, Save } from 'lucide-react';

const businessPlanSchema = z.object({
	businessPlan: z.string().min(1, 'Business plan is required'),
});

type BusinessPlanData = z.infer<typeof businessPlanSchema>;

export function BusinessPlan() {
	const [isSubmitting, setIsSubmitting] = useState(false);

	const form = useForm<BusinessPlanData>({
		resolver: zodResolver(businessPlanSchema),
		defaultValues: {
			businessPlan: '',
		},
	});

	const onSubmit = async (data: BusinessPlanData) => {
		setIsSubmitting(true);
		try {
			// TODO: Implement API call to save business plan
			console.log('Business plan:', data);
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 1000));
			// TODO: Show success message
		} catch (error) {
			console.error('Failed to save business plan:', error);
			// TODO: Show error message
		} finally {
			setIsSubmitting(false);
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
					<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
						<div>
							<label htmlFor="businessPlan" className="block text-sm font-medium mb-2">
								Business Plan *
							</label>
							<Textarea
								id="businessPlan"
								{...form.register('businessPlan')}
								placeholder="Describe your business model, target market, competitive advantages, revenue streams, marketing strategy, operational plan, financial projections, and growth strategy..."
								rows={12}
								className={form.formState.errors.businessPlan ? 'border-red-500' : ''}
							/>
							{form.formState.errors.businessPlan && (
								<p className="text-red-500 text-sm mt-1">
									{form.formState.errors.businessPlan.message}
								</p>
							)}
							<p className="text-sm text-muted-foreground mt-2">
								Include key sections like: Executive Summary, Company Description, Market Analysis, Organization & Management, Service/Product Line, Marketing & Sales Strategy, Funding Requirements, Financial Projections, and Appendix.
							</p>
						</div>

						<div className="flex justify-end">
							<Button type="submit" disabled={isSubmitting}>
								<Save className="h-4 w-4 mr-2" />
								{isSubmitting ? 'Saving...' : 'Save Business Plan'}
							</Button>
						</div>
					</form>
				</CardContent>
			</Card>
		</div>
	);
}
