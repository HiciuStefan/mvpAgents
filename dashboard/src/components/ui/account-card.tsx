import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { ArrowRight } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface AccountCardProps {
	href: string;
	icon: LucideIcon;
	iconBgColor: string;
	iconShadowColor: string;
	title: string;
	description: string;
	features: string[];
	featureDotColor: string;
}

export function AccountCard({
	href,
	icon: Icon,
	iconBgColor,
	iconShadowColor,
	title,
	description,
	features,
	featureDotColor
}: AccountCardProps) {
	return (
		<Link href={href} className="group">
			<Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl shadow-slate-300/30 hover:shadow-2xl hover:shadow-slate-400/50 transition-all duration-500 cursor-pointer group-hover:border-slate-300 overflow-hidden">
				<div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-gray-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
				<CardHeader className="relative z-10 pb-4">
					<div className="flex items-start justify-between">
						<div className="space-y-3">
							<div className={`inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br ${iconBgColor} rounded-xl shadow-lg ${iconShadowColor}`}>
								<Icon className="h-6 w-6 text-white" />
							</div>
							<div>
								<CardTitle className="text-2xl font-bold text-slate-900 group-hover:text-slate-800 transition-colors duration-300">
									{title}
								</CardTitle>
								<CardDescription className="text-slate-600 text-base leading-relaxed mt-2">
									{description}
								</CardDescription>
							</div>
						</div>
						<ArrowRight className="h-6 w-6 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all duration-300" />
					</div>
				</CardHeader>
				<CardContent className="relative z-10 pt-0">
					<div className="space-y-3">
						{features.map((feature, index) => (
							<div key={index} className="flex items-center space-x-2 text-sm text-slate-500">
								<div className={`w-2 h-2 ${featureDotColor} rounded-full`} />
								<span>{feature}</span>
							</div>
						))}
					</div>
				</CardContent>
			</Card>
		</Link>
	);
}
