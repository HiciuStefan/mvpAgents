'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '~/components/ui/form';
import { partnerFormSchema, type PartnerFormData } from '~/server/db/schema';
import { PartnerList } from './_components/PartnerList';

// Mock data - replace with real data later
const mockPartners = [
	{
		id: '1',
		name: 'TechCorp Solutions',
		description: 'Leading technology solutions provider specializing in enterprise software development and digital transformation services.',
		created_at: new Date('2024-01-15'),
	},
	{
		id: '2',
		name: 'GreenEnergy Partners',
		description: 'Renewable energy consulting firm helping businesses transition to sustainable energy solutions.',
		created_at: new Date('2024-01-20'),
	},
	{
		id: '3',
		name: 'DataFlow Analytics',
		description: 'Advanced data analytics and business intelligence solutions for modern enterprises.',
		created_at: new Date('2024-02-01'),
	},
];

export default function AccountPage() {
	const [partners, setPartners] = useState(mockPartners);
	const [isSubmitting, setIsSubmitting] = useState(false);

	const form = useForm<PartnerFormData>({
		resolver: zodResolver(partnerFormSchema),
		defaultValues: {
			name: '',
			description: undefined,
		},
	});

	const onSubmit = async (data: PartnerFormData) => {
		setIsSubmitting(true);

		try {
			// Simulate API call - replace with real API later
			await new Promise(resolve => setTimeout(resolve, 1000));

			const newPartner = {
				id: Date.now().toString(),
				name: data.name,
				description: data.description ?? '',
				created_at: new Date(),
			};

			setPartners(prev => [newPartner, ...prev]);
			form.reset();
		} catch (error) {
			console.error('Failed to create partner:', error);
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<div className="container mx-auto py-8">
			<div className="max-w-4xl mx-auto space-y-8">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Account Settings</h1>
					<p className="text-muted-foreground">
						Manage your account settings and partner relationships.
					</p>
				</div>

				<div className="grid gap-8 md:grid-cols-2">
					{/* Partner Form */}
					<Card>
						<CardHeader>
							<CardTitle>Add New Partner</CardTitle>
							<CardDescription>
								Create a new partner relationship by providing their details below.
							</CardDescription>
						</CardHeader>
						<CardContent>
							<Form {...form}>
								<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
									<FormField
										control={form.control}
										name="name"
										render={({ field }) => (
											<FormItem>
												<FormLabel>Partner Name</FormLabel>
												<FormControl>
													<Input placeholder="Enter partner name" {...field} />
												</FormControl>
												<FormMessage />
											</FormItem>
										)}
									/>
									<FormField
										control={form.control}
										name="description"
										render={({ field }) => (
											<FormItem>
												<FormLabel>Description (Optional)</FormLabel>
												<FormControl>
													<Textarea
														placeholder="Describe the partnership, services, or relationship..."
														className="min-h-[100px]"
														{...field}
													/>
												</FormControl>
												<FormMessage />
											</FormItem>
										)}
									/>
									<Button type="submit" disabled={isSubmitting} className="w-full">
										{isSubmitting ? 'Creating Partner...' : 'Add Partner'}
									</Button>
								</form>
							</Form>
						</CardContent>
					</Card>

					{/* Partner List */}
					<Card>
						<CardHeader>
							<CardTitle>Your Partners</CardTitle>
							<CardDescription>
								Click on any partner to view their details and manage the relationship.
							</CardDescription>
						</CardHeader>
						<CardContent>
							<PartnerList partners={partners} />
						</CardContent>
					</Card>
				</div>
			</div>
		</div>
	);
}
