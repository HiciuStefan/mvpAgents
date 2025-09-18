"use client";

import { useRouter } from "next/navigation";
import { api } from "~/trpc/react";
import { Button } from "~/components/ui/button";
import { useState } from "react";
import {
	Select,
	SelectTrigger,
	SelectValue,
	SelectContent,
	SelectGroup,
	SelectItem,
} from "~/components/ui/select";
import { ArrowLeft } from "lucide-react";

const urgencyOptions = [
	{ value: 0, label: "None" },
	{ value: 1, label: "Low" },
	{ value: 2, label: "Medium" },
	{ value: 3, label: "High" },
];

export default function ItemActions({ id, currentUrgency, refOrigin }: { id: string; currentUrgency: number; refOrigin?: string }) {
	const router = useRouter();
	const utils = api.useUtils();
	const [urgency, setUrgency] = useState<number>(currentUrgency);
	const { mutate: updateUrgency } = api.processed_items.updateUrgency.useMutation({
		onSuccess: async () => {
			await utils.processed_items.invalidate();
			router.refresh();
		},
	});

	function handleBack() {
		if (refOrigin) {
			router.push(`/${refOrigin}`);
			return;
		}
		if (typeof window !== "undefined" && window.history.length > 1) {
			router.back();
			return;
		}
		router.push("/business-intelligence");
	}

	function handleUrgencyChange(value: string) {
		const num = Number(value);
		setUrgency(num);
		updateUrgency({ id, urgency: num });
	}

	return (
		<div className="flex items-center justify-between gap-3">
			<div className="flex items-center">
				{refOrigin && (
					<Button variant="ghost" onClick={handleBack} className="gap-2 px-1 cursor-pointer">
						<ArrowLeft className="size-4" />
						<span>Back</span>
					</Button>
				)}
			</div>
			<div className="flex items-center gap-3">
				<div className="flex items-center gap-2">
					<label className="text-sm font-medium text-gray-900">Urgency</label>
					<Select value={String(urgency)} onValueChange={handleUrgencyChange}>
						<SelectTrigger className="w-[160px]">
							<SelectValue placeholder="Select urgency" />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								{urgencyOptions.map((o) => (
									<SelectItem key={o.value} value={String(o.value)}>
										{o.label}
									</SelectItem>
								))}
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
			</div>
		</div>
	);
}