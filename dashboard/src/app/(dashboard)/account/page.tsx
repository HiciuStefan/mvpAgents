'use client'

import { Building, FileText, Mail, Users, Sparkles, Shield, Zap, Target } from 'lucide-react';
import { AccountCard } from '~/components/ui/account-card';

export default function AccountPage() {
	return (
		<div className="w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
			{/* Background Pattern */}
			<div 
				className="absolute inset-0 -z-10 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] pointer-events-none"
				style={{
					backgroundImage: `
						linear-gradient(to right, rgb(241 245 249 / 0.1) 1px, transparent 1px),
						linear-gradient(to bottom, rgb(241 245 249 / 0.1) 1px, transparent 1px)
					`,
					backgroundSize: '24px 24px'
				}}
			/>

			<div className="relative z-10 container mx-auto py-12 px-4">
				<div className="max-w-7xl mx-auto space-y-12">
					{/* Hero Header */}
					<div className="text-center space-y-6">
						<div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 rounded-3xl shadow-2xl shadow-blue-500/30 mb-8 relative overflow-hidden">
							{/* Animated background elements */}
							<div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-400/20 animate-pulse" />
							<div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-blue-300 to-blue-400 rounded-full opacity-60 animate-bounce" style={{ animationDelay: '0.5s' }} />
							<div className="absolute -bottom-2 -left-2 w-6 h-6 bg-gradient-to-br from-purple-300 to-purple-400 rounded-full opacity-60 animate-bounce" style={{ animationDelay: '1s' }} />

							{/* Main icon with enhanced styling */}
							<div className="relative z-10">
								<div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/30 relative overflow-hidden">
									{/* Custom geometric pattern */}
									<div className="absolute inset-0 flex items-center justify-center">
										<div className="w-8 h-8 relative">
											{/* Diamond shape */}
											<div className="absolute inset-0 bg-white rotate-45 transform scale-75 opacity-90" />
											{/* Inner circle */}
											<div className="absolute inset-1 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full" />
											{/* Center dot */}
											<div className="absolute inset-2 bg-white rounded-full" />
											{/* Corner accents */}
											<div className="absolute -top-1 -left-1 w-2 h-2 bg-blue-300 rounded-full opacity-80" />
											<div className="absolute -top-1 -right-1 w-2 h-2 bg-purple-300 rounded-full opacity-80" />
											<div className="absolute -bottom-1 -left-1 w-2 h-2 bg-purple-300 rounded-full opacity-80" />
											<div className="absolute -bottom-1 -right-1 w-2 h-2 bg-blue-300 rounded-full opacity-80" />
										</div>
									</div>
								</div>
							</div>
						</div>
						
						<div className="space-y-4">
							<h1 className="text-5xl md:text-6xl font-bold tracking-tight bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
								Account Center
							</h1>
							<p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
								Manage your business identity, strategy, and integrations with precision and ease
							</p>
						</div>

						{/* Stats Bar */}
						<div className="flex items-center justify-center space-x-8 pt-4">
							<div className="flex items-center space-x-2 text-slate-600">
								<Sparkles className="h-4 w-4 text-amber-500" />
								<span className="text-sm font-medium">4 Core Areas</span>
							</div>
							<div className="w-px h-4 bg-slate-300" />
							<div className="flex items-center space-x-2 text-slate-600">
								<Shield className="h-4 w-4 text-emerald-500" />
								<span className="text-sm font-medium">Enterprise Security</span>
							</div>
							<div className="w-px h-4 bg-slate-300" />
							<div className="flex items-center space-x-2 text-slate-600">
								<Zap className="h-4 w-4 text-blue-500" />
								<span className="text-sm font-medium">AI-Powered</span>
							</div>
						</div>
					</div>

					{/* Navigation Cards Grid */}
					<div className="grid grid-cols-1 md:grid-cols-2 gap-8">
						<AccountCard
							href="/account/section?section=company"
							icon={Building}
							iconBgColor="from-blue-500 to-blue-600"
							iconShadowColor="shadow-blue-500/25"
							title="Company Profile"
							description="Establish your business identity with comprehensive company details, industry positioning, and strategic location mapping."
							features={[
								"Company name & industry",
								"Location & website",
								"Mission & description"
							]}
							featureDotColor="bg-blue-400"
						/>

						<AccountCard
							href="/account/section?section=business-plan"
							icon={FileText}
							iconBgColor="from-emerald-500 to-emerald-600"
							iconShadowColor="shadow-emerald-500/25"
							title="Business Strategy"
							description="Craft your comprehensive business plan with strategic insights, market analysis, and growth roadmaps."
							features={[
								"Executive summary",
								"Market analysis",
								"Financial projections"
							]}
							featureDotColor="bg-emerald-400"
						/>

						<AccountCard
							href="/account/section?section=gmail"
							icon={Mail}
							iconBgColor="from-red-500 to-red-600"
							iconShadowColor="shadow-red-500/25"
							title="Email Intelligence"
							description="Connect your Gmail for AI-powered email analysis, automated insights, and intelligent response suggestions."
							features={[
								"Smart email processing",
								"AI insights & replies",
								"Performance analytics"
							]}
							featureDotColor="bg-red-400"
						/>

						<AccountCard
							href="/account/section?section=partners"
							icon={Users}
							iconBgColor="from-purple-500 to-purple-600"
							iconShadowColor="shadow-purple-500/25"
							title="Partnership Hub"
							description="Manage strategic partnerships, track collaborations, and optimize your business network relationships."
							features={[
								"Partner management",
								"Collaboration tracking",
								"Network analytics"
							]}
							featureDotColor="bg-purple-400"
						/>
					</div>

					{/* Bottom CTA Section */}
					<div className="text-center space-y-6 pt-8">
						<div className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-slate-900 to-slate-800 rounded-full text-white shadow-xl shadow-slate-900/25">
							<Target className="h-5 w-5 text-blue-400" />
							<span className="font-medium">Ready to optimize your business?</span>
						</div>
						<p className="text-slate-600 max-w-2xl mx-auto">
							Each section is designed to work seamlessly together, creating a comprehensive business management ecosystem that grows with your company.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
