'use client';

import { useRouter } from 'next/navigation';
import { Button } from '~/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Calendar, Users, ArrowRight } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Partner {
	id: string;
	name: string;
	description: string;
	created_at: Date;
}

interface PartnerListProps {
	partners: Partner[];
}

export function PartnerList({ partners }: PartnerListProps) {
	const router = useRouter();

	const handlePartnerClick = (partnerId: string) => {
		router.push(`/account/partners/${partnerId}`);
	};

	if (partners.length === 0) {
		return (
			<div className="text-center py-8">
				<Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
				<h3 className="text-lg font-medium mb-2">No partners yet</h3>
				<p className="text-muted-foreground">
					Create your first partner using the form to get started.
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
					onClick={() => handlePartnerClick(partner.id)}
				>
					<CardHeader className="pb-3">
						<div className="flex items-start justify-between">
							<div className="space-y-1">
								<CardTitle className="text-lg">{partner.name}</CardTitle>
								<div className="flex items-center gap-2 text-sm text-muted-foreground">
									<Calendar className="h-4 w-4" />
									<span>Added {formatDistanceToNow(partner.created_at, { addSuffix: true })}</span>
								</div>
							</div>
							<Button variant="ghost" size="sm">
								<ArrowRight className="h-4 w-4" />
							</Button>
						</div>
					</CardHeader>
					<CardContent>
						<CardDescription className="line-clamp-3">
							{partner.description || 'No description provided.'}
						</CardDescription>
						<div className="flex items-center justify-between mt-4">
							<Badge variant="secondary">Active Partner</Badge>
							<Button
								variant="ghost"
								size="sm"
								onClick={(e: React.MouseEvent) => {
									e.stopPropagation();
									handlePartnerClick(partner.id);
								}}
							>
								View Details
							</Button>
						</div>
					</CardContent>
				</Card>
			))}
		</div>
	);
}
