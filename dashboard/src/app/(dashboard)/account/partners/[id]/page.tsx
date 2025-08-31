import Link from 'next/link';
import { Button } from '~/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { api } from '~/trpc/server';
import { PartnerDetailsClient } from './PartnerDetailsClient';

interface PartnerDetailsPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function PartnerDetailsPage({
  params,
}: PartnerDetailsPageProps) {
  const { id: partnerId } = await params;

  // Fetch partner from database using tRPC
  let partner;
  try {
    partner = await api.partners.getById({ id: partnerId });
  } catch (error) {
    console.error('Error fetching partner:', error);
    partner = null;
  }

  if (!partner) {
    return (
      <div className="container mx-auto py-8">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-2xl font-bold mb-4">Partner Not Found</h1>
          <p className="text-muted-foreground mb-6">
            The partner you&apos;re looking for doesn&apos;t exist or has been
            removed.
          </p>
          <Link href="/account/section?section=partners">
            <Button>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Partners
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return <PartnerDetailsClient partner={partner} />;
}
