import { desc, inArray, eq, and, gte } from 'drizzle-orm';
import { email, processed_items, twitter, website } from './schema';
import { db } from '.';

// Define types for each table's data
type WebsiteData = typeof website.$inferSelect;
type EmailData = typeof email.$inferSelect;
type TwitterData = typeof twitter.$inferSelect;

// Define base processed item type
type ProcessedItem = typeof processed_items.$inferSelect;




// Define discriminated union for return type
export type LatestItem =
{ type: 'website'; data: WebsiteData } & ProcessedItem  |
{ type: 'email'; data: EmailData } & ProcessedItem |
{ type: 'twitter'; data: TwitterData } & ProcessedItem




export async function fetch_latest_items({
	limit = 10,
	actionable = false,
}): Promise<LatestItem[]> {
	// Step 1: Get the latest 10 processed items
	const latestItems = await db
		.select()
		.from(processed_items)
		.where(actionable === true ? eq(processed_items.actionable, true) : undefined)
		.orderBy(desc(processed_items.created_at))
		.limit(limit);


	// Step 2: Split by type
	const websiteIds = latestItems.filter(i => i.type === 'website').map(i => i.id);
	const emailIds   = latestItems.filter(i => i.type === 'email').map(i => i.id);
	const twitterIds = latestItems.filter(i => i.type === 'twitter').map(i => i.id);

	// Step 3: Fetch child data by type
	const [websiteData, emailData, twitterData] = await Promise.all([
		websiteIds.length > 0
			? db.select().from(website).where(inArray(website.processed_item_id, websiteIds))
			: Promise.resolve([]),
		emailIds.length > 0
			? db.select().from(email).where(inArray(email.processed_item_id, emailIds))
			: Promise.resolve([]),
		twitterIds.length > 0
			? db.select().from(twitter).where(inArray(twitter.processed_item_id, twitterIds))
			: Promise.resolve([]),
	]);


	// Step 4: Merge data
	return latestItems.map(item => {
		if (item.type === 'website') {
			return {
				...item,
				data: websiteData.find(w => w.processed_item_id === item.id),
			} as LatestItem;
		}
		if (item.type === 'email') {
			return {
				...item,
				data: emailData.find(e => e.processed_item_id === item.id),
			} as LatestItem;
		}
		if (item.type === 'twitter') {
			return {
				...item,
				data: twitterData.find(t => t.processed_item_id === item.id),
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
		eq(processed_items.type, type),
		gte(processed_items.created_at, startOfToday)
	];

	if (actionable === true) {
		whereConditions.push(eq(processed_items.actionable, true));
	}

	const latestItems = await db
		.select()
		.from(processed_items)
		.where(and(...whereConditions))
		.orderBy(desc(processed_items.created_at))
		.limit(limit);

	// Step 2: Get IDs for the specific type
	const itemIds = latestItems.map(i => i.id);

	// Step 3: Fetch child data based on type
	if (type === 'website') {
		const websiteData = itemIds.length > 0
			? await db.select().from(website).where(inArray(website.processed_item_id, itemIds))
			: [];

		return latestItems.map(item => ({
			...item,
			data: websiteData.find(w => w.processed_item_id === item.id),
		})) as LatestItem[];
	}

	if (type === 'email') {
		const emailData = itemIds.length > 0
			? await db.select().from(email).where(inArray(email.processed_item_id, itemIds))
			: [];

		return latestItems.map(item => ({
			...item,
			data: emailData.find(e => e.processed_item_id === item.id),
		})) as LatestItem[];
	}

	if (type === 'twitter') {
		const twitterData = itemIds.length > 0
			? await db.select().from(twitter).where(inArray(twitter.processed_item_id, itemIds))
			: [];

		return latestItems.map(item => ({
			...item,
			data: twitterData.find(t => t.processed_item_id === item.id),
		})) as LatestItem[];
	}

	return [];
}