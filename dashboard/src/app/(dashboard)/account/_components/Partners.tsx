'use client'

import { useState, Suspense } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { partnerFormSchema, type PartnerFormData } from '~/server/db/schemas/partners';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Card, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Separator } from '~/components/ui/separator';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '~/components/ui/sheet';
import { Plus, Users } from 'lucide-react';
import { PartnersList } from '~/components/partners/PartnersList';
import { api } from '~/trpc/react';

export function Partners() {
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [isOpen, setIsOpen] = useState(false);

	const form = useForm<PartnerFormData>({
		resolver: zodResolver(partnerFormSchema),
		defaultValues: {
			name: '',
			description: undefined,
		},
	});

	const utils = api.useUtils();

	const createPartner = api.partners.create.useMutation({
		onSuccess: () => {
			form.reset();
			setIsOpen(false);
			// Manually invalidate the partners list to trigger a refetch
			void utils.partners.getAll.invalidate();
		},
	});

	const onSubmit = async (data: PartnerFormData) => {
		setIsSubmitting(true);

		try {
			// Transform the form data to match the API input
			await createPartner.mutateAsync({
				name: data.name,
				description: data.description,
			});
		} catch (error) {
			console.error('Failed to create partner:', error);
		} finally {
			setIsSubmitting(false);
		}
	};

	const handleOpenChange = (open: boolean) => {
		setIsOpen(open);
		if (!open) {
			form.reset();
		}
	};

	return (
		<div className="space-y-6">
			{/* Add Partner Button and Sheet */}
			<Card>
				<CardHeader>
					<div className="flex items-center justify-between">
						<div>
							<CardTitle className="flex items-center space-x-2">
								<Plus className="h-5 w-5" />
								<span>Partnership Management</span>
							</CardTitle>
							<CardDescription>
								Add new partnerships and manage existing ones.
							</CardDescription>
						</div>
						<Sheet open={isOpen} onOpenChange={handleOpenChange}>
							<SheetTrigger asChild>
								<Button>
									<Plus className="h-4 w-4 mr-2" />
									Add Partner
								</Button>
							</SheetTrigger>
							<SheetContent className="w-[400px] sm:w-[540px]">
								<SheetHeader>
									<SheetTitle>Add New Partner</SheetTitle>
									<SheetDescription>
										Create a new partnership to track and manage.
									</SheetDescription>
								</SheetHeader>
								<div className="mt-6 px-4">
									<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
										<div>
											<label htmlFor="name" className="block text-sm font-medium mb-2">
												Partner Name *
											</label>
											<Input
												id="name"
												{...form.register('name')}
												placeholder="Enter partner name"
												className={form.formState.errors.name ? 'border-red-500' : ''}
											/>
											{form.formState.errors.name && (
												<p className="text-red-500 text-sm mt-1">
													{form.formState.errors.name.message}
												</p>
											)}
										</div>

										<div>
											<label htmlFor="description" className="block text-sm font-medium mb-2">
												Description
											</label>
											<Textarea
												id="description"
												{...form.register('description')}
												placeholder="Describe the partnership (optional)"
												rows={3}
											/>
											{form.formState.errors.description && (
												<p className="text-red-500 text-sm mt-1">
													{form.formState.errors.description.message}
												</p>
											)}
										</div>

										<div className="flex justify-end space-x-2 pt-4">
											<Button
												type="button"
												variant="outline"
												onClick={() => handleOpenChange(false)}
											>
												Cancel
											</Button>
											<Button type="submit" disabled={isSubmitting}>
												{isSubmitting ? 'Creating...' : 'Create Partner'}
											</Button>
										</div>
									</form>
								</div>
							</SheetContent>
						</Sheet>
					</div>
				</CardHeader>
			</Card>

			<Separator />

			{/* Partners List */}
			<div>
				<div className="flex items-center space-x-2 mb-6">
					<Users className="h-5 w-5 text-muted-foreground" />
					<h2 className="text-2xl font-semibold">Your Partners</h2>
				</div>
				<Suspense fallback={<div className="text-center py-8">Loading partners...</div>}>
					<PartnersList />
				</Suspense>
			</div>
		</div>
	);
}
