import { notFound } from "next/navigation";
import { api } from "~/trpc/server";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "~/components/ui/card";
import { ChannelBadge, XSVG } from "~/components/ChannelBadge";
import { format } from "date-fns";
import ItemActions from "./ClientActions";
import { Badge } from "~/components/ui/badge";
import { CopyButton } from "~/components/CopyButton";
import { CollapsibleText } from "~/components/CollapsibleText";
import { Globe, Mail, Info } from "lucide-react";
import { SparkleSVG } from "~/components/cards/ItemCard";
import SuggestedReplySection from "./SuggestedReplySection";
import { AppSidebar } from "~/components/sidebar/app-sidebar";


export const dynamic = 'force-dynamic';

export default async function ItemDetailPage({ params, searchParams }: { params: Promise<{ id: string }>, searchParams: Promise<{ ref?: string }> }) {
	const { id } = await params;
	const { ref } = await searchParams;

	const item = await api.processed_items.getById({ id });
	if (!item) {
		notFound();
	}

	const createdAt = item.created_at ? new Date(item.created_at) : undefined;
	const readableDate = createdAt ? format(createdAt, "PPpp") : "";

	const urgencyLabel = ["None", "Low", "Medium", "High"][item.urgency] ?? "None";
	const actionableLabel = item.actionable ? "Actionable" : "Informative";

	return (
		<>
			<AppSidebar refParam={ref} />
			<div className="flex flex-col w-6xl gap-5 p-20 pt-8 font-[family-name:var(--font-geist-sans)]">
				<ItemActions id={id} currentUrgency={item.urgency} refOrigin={ref} />

				<Card className="w-full">
					<CardHeader className="border-b">
						<div className="flex items-start justify-between">
							<div className="flex items-center gap-3">
								<CardTitle className="text-xl">{item.client_name}</CardTitle>
								<ChannelBadge type={item.type} />
							</div>
							<CardDescription>{readableDate}</CardDescription>
						</div>
						<div className="mt-3 flex flex-wrap items-center gap-2">
							<Badge variant="secondary">{actionableLabel}</Badge>
							<Badge
								className={
									item.urgency === 3
										? " bg-red-100 text-red-700"
										: item.urgency === 2
										? " bg-yellow-100 text-yellow-700"
										: item.urgency === 1
										? " bg-green-100 text-green-700"
										: " bg-gray-100 text-gray-600"
								}
							>
								Urgency: {urgencyLabel}
							</Badge>
						</div>
					</CardHeader>

					<CardContent>
						<div className="grid grid-cols-1 gap-6">
							<div className="space-y-6">
								<div className="space-y-3">
									<div className="text-lg font-medium flex items-center gap-2">
										<Info className="size-4 text-gray-500" />
										<span>{item.data.short_description}</span>
									</div>
									{item.actionable && item.data.relevance && (
										<CollapsibleText text={item.data.relevance} collapsedLines={6} />
									)}
								</div>

								{/* Type-specific details */}
								<div className="rounded-lg border bg-white">
									<div className="px-4 py-3 w-full border-b text-sm font-medium text-gray-700 flex items-center gap-2">
										<div className="w-6 h-6 flex items-center justify-center text-gray-500">
											{item.type === 'website' && <Globe className="size-4" />}
											{item.type === 'email' && <Mail className="size-4" />}
											{item.type === 'twitter' && <XSVG size={13} />}
										</div>
										<span>Details</span>
									</div>
									<div className="p-4 space-y-3 text-sm">
										{item.type === 'website' && (
											<div className="space-y-2">
												<div className="break-all flex items-center justify-between gap-2">
													<div>URL: <a href={item.data.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{item.data.url}</a></div>
													<CopyButton value={item.data.url} />
												</div>
												<div>Title: {item.data.title}</div>
												<CollapsibleText text={item.data.content} collapsedLines={10} />
											</div>
										)}
										{item.type === 'email' && (
											<div className="space-y-2">
												<div className="flex items-center justify-between">
													<div>Subject: {item.data.subject}</div>
													<CopyButton value={item.data.subject} />
												</div>
												<div>Type: {item.data.type}</div>
												<CollapsibleText text={item.data.content} collapsedLines={12} />
											</div>
										)}
										{item.type === 'twitter' && (
											<div className="space-y-2">
												<div className="flex items-center justify-between gap-2">
													<div>URL: <a href={item.data.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{item.data.url}</a></div>
													<CopyButton value={item.data.url} />
												</div>
												<CollapsibleText text={item.data.text} collapsedLines={8} />
											</div>
										)}
									</div>
								</div>
							</div>

							{item.actionable && "suggested_action" in item.data && item.data.suggested_action && (
								<div className="p-3 rounded-md bg-blue-50 flex items-center gap-2 text-[#1b4fb3] font-medium text-md">
									<SparkleSVG	size={16} />
									<span>{item.data.suggested_action}</span>
								</div>
							)}
						</div>
					</CardContent>

					{/* Suggested Reply Section */}
					{item.actionable &&item.data?.suggested_action && (
						<div className="px-6 pb-6">
							<SuggestedReplySection item={item} />
						</div>
					)}

					<CardFooter className="border-t justify-start gap-2">
						<button className="inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground px-4 h-9 text-sm font-medium opacity-60 cursor-not-allowed" disabled>
							Create Task (soon)
						</button>
					</CardFooter>
				</Card>
			</div>
		</>
	);
}