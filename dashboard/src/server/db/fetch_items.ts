import { desc, inArray, eq, and, gte } from 'drizzle-orm';
import { email, twitter, website } from './schema';
import { db } from '.';
import { startOfToday } from 'date-fns';
import { subDays } from 'date-fns';
import type { DateRangeValueType } from '~/components/filters/date_ranges';
import type { ChannelValueType } from '~/components/filters/channel_ranges';
import { processedItems } from './schemas/processed-items';


// Define types for each table's data
type WebsiteData = typeof website.$inferSelect;
type EmailData = typeof email.$inferSelect;
type TwitterData = typeof twitter.$inferSelect;

// Define base processed item type
type ProcessedItem = typeof processedItems.$inferSelect;




// Define discriminated union for return type
export type LatestItem =
{ type: 'website'; data: WebsiteData } & ProcessedItem  |
{ type: 'email'; data: EmailData } & ProcessedItem |
{ type: 'twitter'; data: TwitterData } & ProcessedItem




export async function fetch_latest_items({
	limit = 10,
	actionable = false,
	date_range,
	channel,
	// priority
}: {
	limit: number,
	actionable: boolean,
	date_range: DateRangeValueType,
	channel: ChannelValueType,
	// priority: number | 'all'
}): Promise<LatestItem[]> {
	const now = new Date();

	let dateFilter: Date | undefined;
	if (date_range === 'today') {
		dateFilter = startOfToday(); // Midnight today
	} else if (date_range === 'last_week') {
		dateFilter = subDays(now, 7);
	} else if (date_range === 'last_30_days') {
		dateFilter = subDays(now, 30);
	}

	// Compose filters
	const conditions = [];

	if (actionable === true) {
		conditions.push(eq(processedItems.actionable, true));
	}

	if (dateFilter) {
		conditions.push(gte(processedItems.createdAt, dateFilter));
	}

	// Add channel filtering if channel is defined and not "all"
	if (channel && channel !== 'all') {
		conditions.push(eq(processedItems.type, channel));
	}

	// if (priority !== 'all') {
	// 	conditions.push(eq(processed_items.urgency, priority));
	// }


	// Step 1: Get the latest 10 processed items
	const latestItems = await db
		.select()
		.from(processedItems)
		// .where(actionable === true ? eq(processed_items.actionable, true) : undefined)
		.where(conditions.length ? and(...conditions) : undefined)
		.orderBy(desc(processedItems.createdAt))
		.limit(limit);


	// Step 2: Split by type
	const websiteIds = latestItems.filter(i => i.type === 'website').map(i => i.id);
	const emailIds   = latestItems.filter(i => i.type === 'email').map(i => i.id);
	const twitterIds = latestItems.filter(i => i.type === 'twitter').map(i => i.id);

	// Step 3: Fetch child data by type
	const [websiteData, emailData, twitterData] = await Promise.all([
		websiteIds.length > 0
			? db.select().from(website).where(inArray(website.processedItemId, websiteIds))
			: Promise.resolve([]),
		emailIds.length > 0
			? db.select().from(email).where(inArray(email.processedItemId, emailIds))
			: Promise.resolve([]),
		twitterIds.length > 0
			? db.select().from(twitter).where(inArray(twitter.processedItemId, twitterIds))
			: Promise.resolve([]),
	]);


	// Step 4: Merge data
	return latestItems.map(item => {
		if (item.type === 'website') {
			return {
				...item,
				data: websiteData.find(w => w.processedItemId === item.id),
			} as LatestItem;
		}
		if (item.type === 'email') {
			return {
				...item,
				data: emailData.find(e => e.processedItemId === item.id),
			} as LatestItem;
		}
		if (item.type === 'twitter') {
			return {
				...item,
				data: twitterData.find(t => t.processedItemId === item.id),
			} as LatestItem;
		}
		return item as LatestItem; // TypeScript should infer correctly
	});
}

export async function fetch_latest_items_by_type({
	type,
	limit = 10,
	actionable = false,
}: {
	type: ProcessedItem['type'];
	limit?: number;
	actionable?: boolean;
}): Promise<LatestItem[]> {
	// Get start of today (00:00:00)
	const startOfToday = new Date();
	startOfToday.setHours(0, 0, 0, 0);

	// Step 1: Get items of the specified type from today
	const whereConditions = [
		eq(processedItems.type, type),
		gte(processedItems.createdAt, startOfToday)
	];

	if (actionable === true) {
		whereConditions.push(eq(processedItems.actionable, true));
	}

	const latestItems = await db
		.select()
		.from(processedItems)
		.where(and(...whereConditions))
		.orderBy(desc(processedItems.createdAt))
		.limit(limit);

	// Step 2: Get IDs for the specific type
	const itemIds = latestItems.map(i => i.id);

	// Step 3: Fetch child data based on type
	if (type === 'website') {
		const websiteData = itemIds.length > 0
			? await db.select().from(website).where(inArray(website.processedItemId, itemIds))
			: [];

		return latestItems.map(item => ({
			...item,
			data: websiteData.find(w => w.processedItemId === item.id),
		})) as LatestItem[];
	}

	if (type === 'email') {
		const emailData = itemIds.length > 0
			? await db.select().from(email).where(inArray(email.processedItemId, itemIds))
			: [];

		return latestItems.map(item => ({
			...item,
			data: emailData.find(e => e.processedItemId === item.id),
		})) as LatestItem[];
	}

	if (type === 'twitter') {
		const twitterData = itemIds.length > 0
			? await db.select().from(twitter).where(inArray(twitter.processedItemId, itemIds))
			: [];

		return latestItems.map(item => ({
			...item,
			data: twitterData.find(t => t.processedItemId === item.id),
		})) as LatestItem[];
	}

	return [];
}

export async function fetch_item_by_id(id: string): Promise<LatestItem | null> {
	const items = await db
		.select()
		.from(processedItems)
		.where(eq(processedItems.id, id))
		.limit(1);

	const [found] = items;
	if (!found) return null;

	const item = found;

	if (item.type === 'website') {
		const data = await db.select().from(website).where(eq(website.processedItemId, id)).limit(1);
		if (data.length === 0) return null;
		return { ...item, type: 'website', data: data[0] } as LatestItem;
	}
	if (item.type === 'email') {
		const data = await db.select().from(email).where(eq(email.processedItemId, id)).limit(1);
		if (data.length === 0) return null;
		return { ...item, type: 'email', data: data[0] } as LatestItem;
	}
	if (item.type === 'twitter') {
		const data = await db.select().from(twitter).where(eq(twitter.processedItemId, id)).limit(1);
		if (data.length === 0) return null;
		return { ...item, type: 'twitter', data: data[0] } as LatestItem;
	}

	return null;
}