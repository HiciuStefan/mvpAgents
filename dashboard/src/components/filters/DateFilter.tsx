'use client'

import * as React from "react";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectGroup,
  SelectItem,
} from "~/components/ui/select";
import { useFilters } from "~/hooks/use-filters";
import type { DateRangeValueType } from "./date_ranges";
import { DefaultDateRangeValue } from "./date_ranges";


export const dateRanges: { value: DateRangeValueType; label: string }[] = [
  { value: 'today', label: 'Today' },
  { value: 'last_week', label: 'Last Week' },
  { value: 'last_30_days', label: 'Last 30 Days' },
];


export function DateFilter() {
	const { filters, updateFilter } = useFilters()

	const handleValueChange = (value: string) => {
		// If "today" is selected, remove the query param entirely
		if (value === DefaultDateRangeValue) {
			updateFilter('date_range', null)
		} else {
			updateFilter('date_range', value)
		}
	}

	return (
		<div className="flex flex-col space-y-1">
			<label className="text-sm font-medium text-gray-900">Date Range</label>
			<Select
				value={filters.date_range ?? DefaultDateRangeValue}
				onValueChange={handleValueChange}
			>
				<SelectTrigger className="w-[180px]">
					<SelectValue placeholder="Select date range" />
				</SelectTrigger>
				<SelectContent>
					<SelectGroup>
						<SelectItem value="today">Today</SelectItem>
						{dateRanges.filter(range => range.value !== "today").map(range => (
							<SelectItem key={range.value} value={range.value}>
								{range.label}
							</SelectItem>
						))}
					</SelectGroup>
				</SelectContent>
			</Select>
		</div>
	);
}