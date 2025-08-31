'use client'

import { useState } from 'react';
import { api } from '~/trpc/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import { Calendar, ArrowRight, Users } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';

export function PartnersList() {
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data, isLoading, error } = api.partners.getAll.useQuery({
    limit,
    offset: (page - 1) * limit,
  });

  const partners = data?.partners ?? [];
  const total = data?.total ?? 0;
  const hasMore = data?.hasMore ?? false;

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-3">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Error loading partners: {error.message}</p>
      </div>
    );
  }

  if (partners.length === 0) {
    return (
      <div className="text-center py-8">
        <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium mb-2">No partners found</h3>
        <p className="text-muted-foreground">
          Create your first partner to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {partners.map((partner) => (
        <Card
          key={partner.id}
          className="cursor-pointer hover:shadow-md transition-shadow duration-200"
        >
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <CardTitle className="text-lg">{partner.name}</CardTitle>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Added {formatDistanceToNow(partner.createdAt, { addSuffix: true })}</span>
                </div>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href={`/account/partners/${partner.id}`}>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <CardDescription className="line-clamp-3">
              {partner.description ?? 'No description provided.'}
            </CardDescription>
            <div className="flex items-center justify-between mt-4">
              <Badge variant="secondary">Active Partner</Badge>
              <Button variant="ghost" size="sm" asChild>
                <Link href={`/account/partners/${partner.id}`}>
                  View Details
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Pagination */}
      {total > limit && (
        <div className="flex justify-center items-center space-x-2 pt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {Math.ceil(total / limit)}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p + 1)}
            disabled={!hasMore}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
