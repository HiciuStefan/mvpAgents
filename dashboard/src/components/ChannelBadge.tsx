import clsx from "clsx";
import { Mail, Globe, MessageCircle } from "lucide-react";
import type { ProcessedItemType } from "~/server/db/schema";


interface ChannelBadgeProps {
	type: ProcessedItemType | 'whatsapp';
	className?: string;
}

export const typeMap = {
	email: {
		color: "bg-orange-100 text-orange-700",
		icon: <Mail size={14} />,
		label: "Email",
	},
	website: {
		color: "bg-blue-100 text-blue-700",
		icon: <Globe size={14} />,
		label: "Website",
	},
	twitter: {
		color: "bg-neutral-100 text-neutral-700",
		icon: <XSVG size={11} />,
		label: '(Twitter)'
	},
	whatsapp: {
		color: "bg-green-100 text-green-800",
		icon: <MessageCircle size={14} />,
		label: "WhatsApp",
	},
};


export const typeMapNoLabel = {
	email: {
		color: "bg-orange-100 text-orange-700",
		icon: <Mail size={16} strokeWidth={1.5} />,
	},
	website: {
		color: "bg-blue-100 text-blue-700",
		icon: <Globe size={16} strokeWidth={1.5} />,
	},
	twitter: {
		color: "bg-neutral-100 text-neutral-700",
		icon: <XSVG size={14} />,
	},
	whatsapp: {
		color: "bg-green-100 text-green-800",
		icon: <MessageCircle size={16} strokeWidth={1.5} />,
	},
};

export function ChannelBadge({ type, className }: ChannelBadgeProps)
{
	const { color, icon, label } = typeMap[type];

	return (
		<div
			className={clsx(
				"inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap",
				color,
				className
			)}
		>
			<span className="w-4 h-4 flex items-center justify-center">{icon}</span>
			{label}
		</div>
	);
}


export function ChannelBadgeNoLabel({ type, className }: ChannelBadgeProps)
{
	const { icon } = typeMapNoLabel[type];

	return (
		<div
			className={clsx(
				"inline-flex items-center gap-2 w-6 h-6 px-1 py-0.5 rounded-full text-xs font-medium whitespace-nowrap",
				className
			)}
		>
			<span className="w-4 h-4 flex items-center justify-center">{icon}</span>
		</div>
	);
}


function XSVG({ size = 24 })
{
	const original_size = {
		width: 1200,
		height: 1227,
	}

	const scale = size / original_size.width;
	const width = original_size.width * scale;
	const height = original_size.height * scale;


	return (
		<svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" viewBox="0 0 1200 1227"><path fill="#000" d="M714.163 519.284 1160.89 0h-105.86L667.137 450.887 357.328 0H0l468.492 681.821L0 1226.37h105.866l409.625-476.152 327.181 476.152H1200L714.137 519.284h.026ZM569.165 687.828l-47.468-67.894-377.686-540.24h162.604l304.797 435.991 47.468 67.894 396.2 566.721H892.476L569.165 687.854v-.026Z"/></svg>
	)
}