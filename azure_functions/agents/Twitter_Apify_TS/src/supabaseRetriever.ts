import { createClient, SupabaseClient } from '@supabase/supabase-js';

/**
 * Create and return Supabase client
 */
export function getSupabaseClient(): SupabaseClient {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    throw new Error('SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set');
  }

  return createClient(url, key);
}

/**
 * Loads JSON content from a specific item in the 'items' table in Supabase.
 */
export async function loadJsonFromSupabase(itemName: string): Promise<any | null> {
  try {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from('items')
      .select('payload')
      .eq('name', itemName)
      .single();

    if (error) {
      console.error(`Error loading ${itemName} from Supabase:`, error);
      return null;
    }

    if (data && 'payload' in data) {
      return data.payload;
    }

    return null;
  } catch (error) {
    console.error(`Error loading ${itemName} from Supabase:`, error);
    return null;
  }
}

/**
 * Get list of Twitter usernames to monitor from Supabase.
 * Returns list of usernames (without @).
 */
export async function getMonitoredTwitterUsernames(): Promise<string[]> {
  const config = await loadJsonFromSupabase('twitter_config');
  if (!config) {
    return [];
  }

  const usernames: string[] = [];
  const monitoredUrls = config.monitored_urls || [];

  for (const entry of monitoredUrls) {
    const profileUrl = entry.profile_url || '';
    if (!profileUrl) {
      continue;
    }

    // Extract username from URL like "https://x.com/@Lica2216"
    // Handle both x.com and twitter.com
    try {
      // Get last part of URL
      let username = profileUrl.replace(/\/$/, '').split('/').pop();
      if (!username) {
        continue;
      }
      
      // Remove @ if present
      username = username.replace(/^@/, '');
      if (username) {
        usernames.push(username);
      }
    } catch (error) {
      console.error(`Failed to parse URL ${profileUrl}:`, error);
      continue;
    }
  }

  return usernames;
}


