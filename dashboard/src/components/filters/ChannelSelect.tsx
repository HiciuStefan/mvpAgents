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

const channels = ["website", "email", "twitter"];

export function ChannelSelect() {
  return (
    <div className="flex flex-col space-y-1">
      <label className="text-sm font-medium text-gray-900">Channel</label>
      <Select defaultValue="all">
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select a channel" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectItem value="all">All</SelectItem>
            {channels.map(channel => (
              <SelectItem key={channel} value={channel}>
                {channel.charAt(0).toUpperCase() + channel.slice(1)}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  );
} 