"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";

export function CollapsibleText({ text, collapsedLines = 6 }: { text: string; collapsedLines?: number }) {
	const [expanded, setExpanded] = useState(false);
	if (!text) return null;

	return (
		<div className="space-y-1">
			<div className={expanded ? "whitespace-pre-wrap leading-relaxed" : `whitespace-pre-wrap leading-relaxed 
				// line-clamp-${collapsedLines}
				`}>
				{text}
			</div>
			{/* {(text?.length ?? 0) > 220 && (
				<Button type="button" variant="ghost" size="sm" className="h-7 px-2" onClick={() => setExpanded(v => !v)}>
					{expanded ? "Show less" : "Show more"}
				</Button>
			)} */}
		</div>
	);
}