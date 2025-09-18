import Link from 'next/link';
import { Button } from '~/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Separator } from '~/components/ui/separator';
import {
  Calendar,
  Building,
  FileText,
  Edit,
  Trash2,
  ArrowLeft,
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';

// Mock data - replace with real data fetching later
const mockPartners = [
  {
    id: '1',
    name: 'TechCorp Solutions',
    description:
      'Leading technology solutions provider specializing in enterprise software development and digital transformation services. We help businesses modernize their technology stack and improve operational efficiency through cutting-edge software solutions.',
    created_at: new Date('2024-01-15'),
    user_id: 'user-123',
  },
  {
    id: '2',
    name: 'GreenEnergy Partners',
    description:
      'Renewable energy consulting firm helping businesses transition to sustainable energy solutions. Our expertise includes solar panel installations, wind energy consulting, and energy efficiency audits.',
    created_at: new Date('2024-01-20'),
    user_id: 'user-123',
  },
  {
    id: '3',
    name: 'DataFlow Analytics',
    description:
      'Advanced data analytics and business intelligence solutions for modern enterprises. We provide comprehensive data analysis, visualization, and predictive modeling services to help organizations make data-driven decisions.',
    created_at: new Date('2024-02-01'),
    user_id: 'user-123',
  },
];

interface PartnerDetailsPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function PartnerDetailsPage({
  params,
}: PartnerDetailsPageProps) {
  const { id } = await params;

  // Find partner by ID - replace with real data fetching
  const partner = mockPartners.find(p => p.id === id);

  if (!partner) {
    return (
      <div className="container mx-auto py-8">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-2xl font-bold mb-4">Partner Not Found</h1>
          <p className="text-muted-foreground mb-6">
            The partner you&apos;re looking for doesn&apos;t exist or has been
            removed.
          </p>
          <Link href="/account">
            <Button>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Account
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/account">
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
            <Button variant="outline" size="sm">
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
            <Button variant="destructive" size="sm">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
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
                <p className="text-sm">{format(partner.created_at, 'PPP')}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Time Active
                </label>
                <p className="text-sm">
                  {formatDistanceToNow(partner.created_at, { addSuffix: true })}
                </p>
              </div>
            </div>

            <Separator />

            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Description
              </label>
              <div className="prose prose-sm max-w-none">
                <p className="text-sm leading-relaxed">
                  {partner.description || 'No description provided.'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Future Sections - Ready for expansion */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Recent Activity</span>
              </CardTitle>
              <CardDescription>Latest interactions and updates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="mx-auto h-8 w-8 mb-2" />
                <p className="text-sm">No recent activity</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Upcoming Tasks</span>
              </CardTitle>
              <CardDescription>
                Scheduled activities and deadlines
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="mx-auto h-8 w-8 mb-2" />
                <p className="text-sm">No upcoming tasks</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4 pt-6">
          <Link href="/account/partners">
            <Button variant="outline">Back to Partners</Button>
          </Link>
          <Button>Manage Partnership</Button>
        </div>
      </div>
    </div>
  );
}
