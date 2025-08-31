'use client'

import { useState } from 'react';
import { Button } from '~/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Mail, Link, CheckCircle, AlertCircle } from 'lucide-react';

export function GmailConnection() {
	const [isConnecting, setIsConnecting] = useState(false);
	const [isConnected, setIsConnected] = useState(false);

	const handleConnectGmail = async () => {
		setIsConnecting(true);
		try {
			// TODO: Implement Gmail OAuth connection
			console.log('Connecting to Gmail...');
			// Simulate connection process
			await new Promise(resolve => setTimeout(resolve, 2000));
			setIsConnected(true);
			// TODO: Show success message
		} catch (error) {
			console.error('Failed to connect Gmail:', error);
			// TODO: Show error message
		} finally {
			setIsConnecting(false);
		}
	};

	return (
		<div className="space-y-6">
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center space-x-2">
						<Mail className="h-5 w-5" />
						<span>Gmail Integration</span>
					</CardTitle>
					<CardDescription>
						Connect your Gmail account to enable email processing and analysis.
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-6">
					{/* Connection Status */}
					<div className="flex items-center space-x-3">
						<span className="text-sm font-medium">Status:</span>
						{isConnected ? (
							<Badge variant="secondary" className="bg-green-100 text-green-800">
								<CheckCircle className="h-3 w-3 mr-1" />
								Connected
							</Badge>
						) : (
							<Badge variant="secondary" className="bg-gray-100 text-gray-800">
								<AlertCircle className="h-3 w-3 mr-1" />
								Not Connected
							</Badge>
						)}
					</div>

					{/* Connection Button */}
					<div className="flex items-center space-x-4">
						<Button
							onClick={handleConnectGmail}
							disabled={isConnecting || isConnected}
							className="flex items-center space-x-2"
						>
							{isConnecting ? (
								<>
									<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
									<span>Connecting...</span>
								</>
							) : isConnected ? (
								<>
									<CheckCircle className="h-4 w-4" />
									<span>Connected</span>
								</>
							) : (
								<>
									<Link className="h-4 w-4" />
									<span>Connect Gmail</span>
								</>
							)}
						</Button>

						{isConnected && (
							<Button variant="outline" size="sm">
								Disconnect
							</Button>
						)}
					</div>

					{/* Benefits */}
					<div className="bg-muted/50 rounded-lg p-4">
						<h4 className="font-medium mb-3">What you can do with Gmail integration:</h4>
						<ul className="space-y-2 text-sm text-muted-foreground">
							<li className="flex items-center space-x-2">
								<CheckCircle className="h-3 w-3 text-green-600" />
								<span>Automatically process and analyze incoming emails</span>
							</li>
							<li className="flex items-center space-x-2">
								<CheckCircle className="h-3 w-3 text-green-600" />
								<span>Get AI-powered insights and suggested replies</span>
							</li>
							<li className="flex items-center space-x-2">
								<CheckCircle className="h-3 w-3 text-green-600" />
								<span>Track email performance and engagement</span>
							</li>
							<li className="flex items-center space-x-2">
								<CheckCircle className="h-3 w-3 text-green-600" />
								<span>Integrate with your business intelligence dashboard</span>
							</li>
						</ul>
					</div>

					{/* Security Note */}
					<div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
						<div className="flex items-start space-x-2">
							<AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
							<div className="text-sm text-blue-800">
								<strong>Security Note:</strong> We only request read access to your emails for processing and analysis. 
								We never store your email content permanently and all data is encrypted in transit.
							</div>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
