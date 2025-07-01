import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { ChannelBadge } from "~/components/ChannelBadge";
import type { LatestItem } from "~/server/db/fetch_items";


export function ItemCard({ item } : { item: LatestItem })
{
	const { type, data, client_name } = item;
	const { short_description, relevance } = data;

	const suggested_action = 'suggested_action' in data ? data.suggested_action : null;


	return (
		<Card className="flex flex-row w-full">
			<CardHeader className="w-[200px] shrink-0 flex flex-col items-start h-full py-[5px] gap-3">
				<CardTitle>{client_name}</CardTitle>
				<ChannelBadge type={type} />
			</CardHeader>
			<CardContent className="pr-4">
				<div className="flex flex-col items-start gap-1">
					<div>
						<div className="text-lg font-medium">{short_description}</div>
						<div className="mb-4 text-sm text-gray-500">{relevance}</div>
					</div>
					{suggested_action &&
						<div className="flex items-center gap-2 font-medium text-[#1b4fb3]">
							<SparkleSVG size={16} />
							<span>{suggested_action}</span>
						</div>
					}
				</div>
			</CardContent>
		</Card>
	);
}


function SparkleSVG({ size = 24 })
{
	const sizePx = `${size}px`;

	return (
		<svg width={sizePx} height={sizePx} fill="currentColor" viewBox="0 0 551.60144 522.17389" xmlns="http://www.w3.org/2000/svg">
			<g transform="translate(-74.19621 -18.2226)">
				<path d="m624.17 312.34c-1.3789-2.7344-4.7891-4.1055-7.5273-4.7891-15.754 0-151.18-5.4648-151.18-162.8 0-4.7812-4.0977-8.8867-8.9023-8.8867-4.7695 0-8.875 4.1055-8.875 8.8867 0 157.34-135.44 162.8-150.5 162.8-2.0508 0-4.1055.68359-5.4727 2.0547-1.3711.68359-2.0625 2.043-2.7344 2.7344-1.3711 2.7383-1.3711 6.1562 0 8.8945 1.3672 2.7422 4.7812 4.7891 8.2031 4.7891h.68359c15.734 0 150.5 5.4766 150.5 162.8 0 4.7812 4.0977 8.8945 8.8984 8.8945 4.7891 0 8.8828-4.1094 8.8828-8.8945 0-156.64 134.75-162.8 150.5-162.8 3.4141 0 6.1484-2.043 8.2109-4.7891 1.3516-2.7383 1.3516-6.1484-.69141-8.8945z"/>
				<path d="m265.04 424.53c-8.2109 0-82.086-2.7383-82.086-88.93 0-4.793-4.1055-8.8984-8.8867-8.8984-4.7891 0-8.8945 4.0977-8.8945 8.8984 0 86.191-73.875 88.93-82.086 88.93h-.68359c-4.7852.68359-8.207 4.0938-8.207 8.8867s4.1055 8.8984 8.8945 8.8984c8.8945 0 82.086 2.7266 82.086 88.918 0 4.7812 4.1055 8.8984 8.8945 8.8984 4.1055 1.3672 8.2109-2.7344 8.2109-8.2109 0-86.195 73.875-88.93 82.086-88.93h.68359c4.7891 0 8.8945-4.0977 8.8945-9.5742-.0156-4.793-4.1172-8.8867-8.9062-8.8867z"/>
				<path d="m343.7 134.5c4.793 0 8.8984-4.1055 8.8984-9.5742 0-4.7891-4.1055-8.8867-8.8984-8.8867-8.1992 0-82.078-2.7383-82.078-88.922 0-4.7891-4.1055-8.8945-8.8945-8.8945-4.7891 0-8.8867 4.1055-8.8867 8.8945 0 86.191-73.879 88.922-82.086 88.922h-.6875c-4.7891.68359-8.2031 4.0977-8.2031 8.8867s4.1055 8.8945 8.8945 8.8945c8.8945 0 82.086 2.7344 82.086 88.922 0 4.7891 4.0977 8.8945 8.8867 8.8945 4.1055.6875 8.2109-3.4141 8.2109-8.2109 0-86.191 73.871-88.922 82.086-88.922z"/>
			</g>
		</svg>
	)
}