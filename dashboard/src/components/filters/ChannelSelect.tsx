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
import type { ChannelValueType } from "./channel_ranges";

export const channels: { value: ChannelValueType; label: string }[] = [
	{ value: 'all', label: 'All Channels' },
	{ value: 'website', label: 'Website' },
	{ value: 'email', label: 'Email' },
	{ value: 'twitter', label: 'Twitter' },
];

export function ChannelSelect() {
	const { filters, updateFilter } = useFilters()

	const handleValueChange = (value: string) => {
		// If "today" is selected, remove the query param entirely
		if (value === "all") {
			updateFilter('channel', null)
		} else {
			updateFilter('channel', value)
		}
	}
  return (
    <div className="flex flex-col space-y-1">
      <label className="text-sm font-medium text-gray-900">Channel</label>
      <Select value={filters.channel ?? "all"} onValueChange={handleValueChange}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select a channel" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {channels.map(channel => (
              <SelectItem key={channel.value} value={channel.value}>
                {channel.label}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  );
}