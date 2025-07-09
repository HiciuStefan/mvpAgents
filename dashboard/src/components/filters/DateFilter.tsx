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

const dateRanges = [
  { value: "today", label: "Today" },
  { value: "last-week", label: "Last Week" },
  { value: "last-30-days", label: "Last 30 Days" }
];

export function DateFilter() {
  return (
    <div className="flex flex-col space-y-1">
      <label className="text-sm font-medium text-gray-900">Date Range</label>
      <Select defaultValue="today">
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select date range" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {dateRanges.map(range => (
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