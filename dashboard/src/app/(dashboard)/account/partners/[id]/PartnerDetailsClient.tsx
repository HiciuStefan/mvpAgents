'use client'

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { partnerFormSchema, type PartnerFormData } from '~/server/db/schemas/partners';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '~/components/ui/sheet';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '~/components/ui/alert-dialog';
import {
  Building,
  FileText,
  Edit,
  Trash2,
  ArrowLeft,
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import { api } from '~/trpc/react';
import { PartnerContactForm } from '~/components/partners/PartnerContactForm';

type Partner = {
  id: string;
  name: string;
  description: string | null;
  createdAt: Date;
  updatedAt: Date;
};

interface PartnerDetailsClientProps {
  partner: Partner;
}

export function PartnerDetailsClient({ partner }: PartnerDetailsClientProps) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);

  const utils = api.useUtils();

  const form = useForm<PartnerFormData>({
    resolver: zodResolver(partnerFormSchema),
    defaultValues: {
      name: partner.name,
      description: partner.description ?? undefined,
    },
  });

  const updatePartner = api.partners.update.useMutation({
    onSuccess: () => {
      // Invalidate the partners list for other components
      void utils.partners.getAll.invalidate();
      setIsEditOpen(false);
      // Force a page refresh to get the latest server data
      router.refresh();
    },
  });

  const deletePartner = api.partners.delete.useMutation({
    onSuccess: () => {
      // Invalidate the partners list and redirect to partners section
      void utils.partners.getAll.invalidate();
      router.push('/account/section?section=partners');
    },
  });

  const handleEdit = async (data: PartnerFormData) => {
    try {
      await updatePartner.mutateAsync({
        id: partner.id,
        data: {
          name: data.name,
          description: data.description,
        },
      });
    } catch (error) {
      console.error('Failed to update partner:', error);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deletePartner.mutateAsync({ id: partner.id });
    } catch (error) {
      console.error('Failed to delete partner:', error);
      setIsDeleting(false);
    }
  };

  const handleEditOpenChange = (open: boolean) => {
    setIsEditOpen(open);
    if (!open) {
      // Reset form to current partner data when closing
      form.reset({
        name: partner.name,
        description: partner.description ?? undefined,
      });
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/account/section?section=partners">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                {partner.name}
              </h1>
              <p className="text-muted-foreground">
                Partner Details &amp; Management
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Sheet open={isEditOpen} onOpenChange={handleEditOpenChange}>
              <SheetTrigger asChild>
                <Button variant="outline" size="sm">
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </Button>
              </SheetTrigger>
              <SheetContent>
                <SheetHeader>
                  <SheetTitle>Edit Partner</SheetTitle>
                  <SheetDescription>
                    Make changes to this partner&apos;s details.
                  </SheetDescription>
                </SheetHeader>
                <div className="py-6 space-y-6 mx-4">
                  <form onSubmit={form.handleSubmit(handleEdit)} className="space-y-4">
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
                        onClick={() => handleEditOpenChange(false)}
                      >
                        Cancel
                      </Button>
                      <Button type="submit" disabled={updatePartner.isPending}>
                        {updatePartner.isPending ? 'Saving...' : 'Save Changes'}
                      </Button>
                    </div>
                  </form>
                </div>
              </SheetContent>
            </Sheet>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Partner</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to delete &quot;{partner.name}&quot;? This action cannot be undone and will permanently remove all partner information.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleDelete}
                    className="bg-red-600 hover:bg-red-700"
                    disabled={isDeleting}
                  >
                    {isDeleting ? 'Deleting...' : 'Delete Partner'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        {/* Partner Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building className="h-5 w-5" />
              <span>Partner Overview</span>
            </CardTitle>
            <CardDescription>
              General information about this partner relationship
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Partner Name
                </label>
                <p className="text-lg font-medium">{partner.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Status
                </label>
                <div className="mt-1">
                  <Badge variant="secondary">Active Partner</Badge>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Relationship Since
                </label>
                <p className="text-sm">{format(partner.createdAt, 'PPP')}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Last Updated
                </label>
                <p className="text-sm">{format(partner.updatedAt, 'PPP')}</p>
              </div>
            </div>

            {partner.description && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Description
                </label>
                <p className="mt-1 text-sm leading-relaxed">
                  {partner.description}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Contact & Social Information Form */}
        <PartnerContactForm />

        {/* Additional sections can be added here */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>Partner Information</span>
            </CardTitle>
            <CardDescription>
              Additional details and notes about this partnership
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Partner ID: {partner.id}
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Created: {formatDistanceToNow(partner.createdAt, { addSuffix: true })}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
