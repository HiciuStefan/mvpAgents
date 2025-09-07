'use client';

import Link from 'next/link';
import { PricingTable, useAuth } from '@clerk/nextjs';
import { Skeleton } from '~/components/ui/skeleton';
import { useRouter } from 'next/navigation';
import { Button } from '~/components/ui/button';
// import { useEffect } from 'react';
// import { ROUTES } from '~/lib/nav_items';

export default function OnboardingPricingPage() {
  const router = useRouter();
  const { orgId } = useAuth();

  // useEffect(() => {
  //   if (!orgId) {
  //     router.push(ROUTES.ONBOARDING.SELECTION);
  //   }
  // }, [orgId, router]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Pricing</h1>
            <p className="text-gray-600">Description</p>
          </div>

          <div className="flex justify-center">
            <PricingTable
              // forOrganizations
              ctaPosition="bottom"
              newSubscriptionRedirectUrl="/dashboard"
              checkoutProps={{
                appearance: {
                  elements: {
                    rootBox: 'w-full max-w-4xl',
                  },
                },
              }}
              fallback={
                <div className="flex justify-center items-center h-64">
                  <div className="text-center space-y-2">
                    <Skeleton className="w-full h-64" />
                  </div>
                </div>
              }
            />
          </div>
          {/* <div className="flex justify-center mt-6">
            <Button asChild>
              <Link href="/">Continue Without Plan</Link>
            </Button>
          </div> */}
        </div>
      </div>
    </div>
  );
}
