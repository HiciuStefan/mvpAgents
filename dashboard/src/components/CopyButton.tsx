"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";
import { Check, Copy } from "lucide-react";

export function CopyButton({ value, label = "Copy" }: { value: string; label?: string }) {
	const [copied, setCopied] = useState(false);

	async function onCopy() {
		try {
			await navigator.clipboard.writeText(value);
			setCopied(true);
			setTimeout(() => setCopied(false), 1200);
		} catch (_) {
			// noop
		}
	}

	return (
		<Button type="button" variant="ghost" size="sm" onClick={onCopy} className="h-7 px-2 gap-1">
			{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
			<span className="text-xs">{copied ? "Copied" : label}</span>
		</Button>
	);
} 