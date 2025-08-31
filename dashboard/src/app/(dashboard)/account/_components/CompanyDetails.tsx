'use client'

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Building, Save } from 'lucide-react';

const companyDetailsSchema = z.object({
	companyName: z.string().min(1, 'Company name is required'),
	companyDetails: z.string().min(1, 'Company details are required'),
	website: z.string().url('Please enter a valid URL').optional().or(z.literal('')),
	industry: z.string().min(1, 'Industry is required'),
	location: z.string().min(1, 'Location is required'),
});

type CompanyDetailsData = z.infer<typeof companyDetailsSchema>;

export function CompanyDetails() {
	const [isSubmitting, setIsSubmitting] = useState(false);

	const form = useForm<CompanyDetailsData>({
		resolver: zodResolver(companyDetailsSchema),
		defaultValues: {
			companyName: '',
			companyDetails: '',
			website: '',
			industry: '',
			location: '',
		},
	});

	const onSubmit = async (data: CompanyDetailsData) => {
		setIsSubmitting(true);
		try {
			// TODO: Implement API call to save company details
			console.log('Company details:', data);
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 1000));
			// TODO: Show success message
		} catch (error) {
			console.error('Failed to save company details:', error);
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
						<Building className="h-5 w-5" />
						<span>Company Information</span>
					</CardTitle>
					<CardDescription>
						Update your company details and information.
					</CardDescription>
				</CardHeader>
				<CardContent>
					<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
						<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<label htmlFor="companyName" className="block text-sm font-medium mb-2">
									Company Name *
								</label>
								<Input
									id="companyName"
									{...form.register('companyName')}
									placeholder="Enter company name"
									className={form.formState.errors.companyName ? 'border-red-500' : ''}
								/>
								{form.formState.errors.companyName && (
									<p className="text-red-500 text-sm mt-1">
										{form.formState.errors.companyName.message}
									</p>
								)}
							</div>

							<div>
								<label htmlFor="industry" className="block text-sm font-medium mb-2">
									Industry *
								</label>
								<Input
									id="industry"
									{...form.register('industry')}
									placeholder="e.g., Technology, Healthcare, Finance"
									className={form.formState.errors.industry ? 'border-red-500' : ''}
								/>
								{form.formState.errors.industry && (
									<p className="text-red-500 text-sm mt-1">
										{form.formState.errors.industry.message}
									</p>
								)}
							</div>
						</div>

						<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<label htmlFor="location" className="block text-sm font-medium mb-2">
									Location *
								</label>
								<Input
									id="location"
									{...form.register('location')}
									placeholder="City, Country"
									className={form.formState.errors.location ? 'border-red-500' : ''}
								/>
								{form.formState.errors.location && (
									<p className="text-red-500 text-sm mt-1">
										{form.formState.errors.location.message}
									</p>
								)}
							</div>

							<div>
								<label htmlFor="website" className="block text-sm font-medium mb-2">
									Website
								</label>
								<Input
									id="website"
									{...form.register('website')}
									placeholder="https://example.com"
									className={form.formState.errors.website ? 'border-red-500' : ''}
								/>
								{form.formState.errors.website && (
									<p className="text-red-500 text-sm mt-1">
										{form.formState.errors.website.message}
									</p>
								)}
							</div>
						</div>

						<div>
							<label htmlFor="companyDetails" className="block text-sm font-medium mb-2">
								Company Details *
							</label>
							<Textarea
								id="companyDetails"
								{...form.register('companyDetails')}
								placeholder="Describe your company, mission, and what you do..."
								rows={4}
								className={form.formState.errors.companyDetails ? 'border-red-500' : ''}
							/>
							{form.formState.errors.companyDetails && (
								<p className="text-red-500 text-sm mt-1">
									{form.formState.errors.companyDetails.message}
								</p>
							)}
						</div>

						<div className="flex justify-end">
							<Button type="submit" disabled={isSubmitting}>
								<Save className="h-4 w-4 mr-2" />
								{isSubmitting ? 'Saving...' : 'Save Company Details'}
							</Button>
						</div>
					</form>
				</CardContent>
			</Card>
		</div>
	);
}
