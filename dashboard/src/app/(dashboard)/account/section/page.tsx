import { redirect } from 'next/navigation';
import { CompanyDetails } from '../_components/CompanyDetails';
import { BusinessPlan } from '../_components/BusinessPlan';
import { GmailConnection } from '../_components/GmailConnection';
import { Partners } from '../_components/Partners';
import { Button } from '~/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default async function AccountSectionPage({
	searchParams,
}: {
	searchParams: Promise<{
		section?: string;
	}>;
}) {
	const sp = await searchParams;
	const section = sp?.section;

	// Redirect to home if no section is specified
	if (!section) {
		redirect('/');
	}

	const renderSection = () => {
		switch (section) {
			case 'company':
				return <CompanyDetails />;
			case 'business-plan':
				return <BusinessPlan />;
			case 'gmail':
				return <GmailConnection />;
			case 'partners':
				return <Partners />;
			default:
				// Redirect to main account page for invalid sections
				redirect('/account');
		}
	};

	const getSectionTitle = () => {
		switch (section) {
			case 'company':
				return 'Company Information';
			case 'business-plan':
				return 'Business Plan';
			case 'gmail':
				return 'Gmail Integration';
			case 'partners':
				return 'Partners';
			default:
				return 'Account Section';
		}
	};

	return (
		<div className="container mx-auto py-8">
			<div className="max-w-6xl mx-auto space-y-6">
				{/* Header with Back Button */}
				<div className="flex items-center space-x-4">
					<Link href="/account">
						<Button variant="outline" size="sm">
							<ArrowLeft className="h-4 w-4 mr-2" />
							Back to Account
						</Button>
					</Link>
					<div className="h-6 w-px bg-border" />
					<h1 className="text-3xl font-bold tracking-tight">{getSectionTitle()}</h1>
				</div>

				{/* Section Content */}
				{renderSection()}
			</div>
		</div>
	);
}
