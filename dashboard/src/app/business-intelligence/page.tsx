import { ItemCard } from "~/components/cards/ItemCard";
import { api } from "~/trpc/server";
import { ClientSelect } from "~/components/filters/ClientSelect";
import { ChannelSelect } from "~/components/filters/ChannelSelect";
import { type DateRangeValueType, DefaultDateRangeValue } from "~/components/filters/date_ranges";
import { DateFilter } from "~/components/filters/DateFilter";
import { DefaultChannelValue, type ChannelValueType } from "~/components/filters/channel_ranges";
import { PriorityFilter } from "~/components/filters/PriorityFilter";

interface PageProps {
	searchParams: Promise<{
	  channel?: ChannelValueType
	  date_range?: DateRangeValueType
	  priority?: string
	}>
  }

// Server-side filter parser
function parseFilters(searchParams: Awaited<PageProps['searchParams']>) {
	return {
	  channel: searchParams.channel ?? DefaultChannelValue,
	  date_range: searchParams.date_range ?? DefaultDateRangeValue,
	  priority: searchParams.priority ? Number(searchParams.priority) as 1 | 2 | 3 : undefined,
	}
  }

export default async function BusinessIntelligence({ searchParams }: PageProps)
{
	const resolvedSearchParams = await searchParams;
	const filters = parseFilters(resolvedSearchParams);

	const latest_items = await api.processed_items.getLatest({
		limit: 100,
		actionable: true,
		channel: filters.channel,
		date_range: filters.date_range,
		// priority: filters.priority ?? 'all',
	});

	const priorities = {
		low: 0,
		medium: 0,
		high: 0,
		new: 0
	}

	latest_items.forEach(item => {
		if (item.urgency === 1) {
			priorities.low++;
		}
		else if (item.urgency === 2) {
			priorities.medium++;
		}
		else if (item.urgency === 3) {
			priorities.high++;
		}

		priorities.new++;
	});


	const clientOptions = Array.from(new Set(latest_items.map(item => item.client_name)));

	const filtered_items = latest_items.filter(item => {
		if (filters.priority !== undefined) {
			return item.urgency === filters.priority;
		}
		return true;
	});

	return (
		<div className="flex flex-col align-middle p-20 pt-8 pr-8 font-[family-name:var(--font-geist-sans)]">
			<h1 className="text-2xl font-semibold text-[26px]">Business Intelligence</h1>
			<p className="text-zinc-500 text-[17px] mb-6">
				Focus on what matters most with filtered insights for smarter business decisions.
			</p>
			<div className="flex space-x-4 mb-8">
				<ClientSelect clients={clientOptions} />
				<ChannelSelect />
				<DateFilter />
			</div>
			<div className="flex items-center gap-1 mt-1 mb-3.5">
				<PriorityFilter priorities={priorities} />
			</div>
			<main className="flex w-5xl flex-col gap-[16px]">
				{filtered_items.map((item, index) => {
					return (
						<ItemCard key={index} item={item} />
					);
				})}
			</main>
		</div>
	);
}
