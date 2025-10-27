import {
  app,
  HttpRequest,
  HttpResponseInit,
  InvocationContext,
} from '@azure/functions';
import axios, { AxiosError } from 'axios';
import * as fs from 'fs/promises';
import * as path from 'path';
import { getMonitoredTwitterUsernames } from '../supabaseRetriever';
import {
  ScrapeTwitterRequest,
  ApifyActorInput,
  ApifyTweetItem,
  Tweet,
  ScrapeResponse,
  ErrorResponse,
} from '../types';

// Apify API Configuration
const APIFY_ACTOR_ID = 'ghSpYIW3L1RvT57NT'; // Twitter Scraper V2
const APIFY_API_BASE = 'https://api.apify.com/v2';
const TIMEOUT_SECONDS = 300000; // 5 minutes in milliseconds

export async function scrapeTwitter(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  context.log('Twitter scraper endpoint called');

  // Get Apify token from environment
  const apifyToken = process.env.APIFY_TOKEN;
  if (!apifyToken) {
    const errorResponse: ErrorResponse = {
      error: 'APIFY_TOKEN not configured',
    };
    return {
      status: 500,
      jsonBody: errorResponse,
    };
  }

  // Parse request body
  let reqBody: ScrapeTwitterRequest = {};
  try {
    const bodyText = await request.text();
    if (bodyText) {
      reqBody = JSON.parse(bodyText);
    }
  } catch (error) {
    context.warn('Failed to parse request body, using empty object');
  }

  // Get username: from request body, or from Supabase, or fallback to hardcoded
  let username = reqBody.username;

  if (!username) {
    // Try to get from Supabase
    context.log('No username in request, fetching from Supabase...');
    try {
      const usernames = await getMonitoredTwitterUsernames();
      if (usernames.length > 0) {
        username = usernames[0]; // Use first monitored username
        context.log(`Found username from Supabase: ${username}`);
      } else {
        username = 'lica2216'; // Final fallback
        context.warn('No usernames in Supabase, using fallback: lica2216');
      }
    } catch (error) {
      context.error('Failed to get usernames from Supabase:', error);
      username = 'lica2216'; // Fallback on error
    }
  }

  // Build actor input - use exact parameters that work in Apify console
  const actorInput: ApifyActorInput = {
    username: username,
    max_posts: reqBody.max_posts || 20,
    search_type: reqBody.search_type || 'Top',
  };

  context.log(`Running Apify scraper with input: ${JSON.stringify(actorInput)}`);

  // Call Apify API (sync mode - wait for results)
  try {
    const url = `${APIFY_API_BASE}/acts/${APIFY_ACTOR_ID}/run-sync-get-dataset-items`;
    const headers = {
      Authorization: `Bearer ${apifyToken}`,
      'Content-Type': 'application/json',
    };

    const response = await axios.post<ApifyTweetItem[]>(url, actorInput, {
      headers,
      timeout: TIMEOUT_SECONDS,
    });

    // Get results
    let items = response.data;
    if (!Array.isArray(items)) {
      items = items ? [items] : [];
    }

    // Filter out demo items and normalize
    const tweets: Tweet[] = [];
    for (const item of items) {
      if (item.demo) {
        continue;
      }

      // Extract author info
      const author = item.author || {};
      const authorName = author.screen_name || author.name || '';
      const tweetId = item.tweet_id || '';

      // Build tweet URL
      const tweetUrl =
        authorName && tweetId
          ? `https://twitter.com/${authorName}/status/${tweetId}`
          : '';

      tweets.push({
        tweet_id: String(tweetId),
        url: tweetUrl,
        text: item.text || '',
        author: authorName,
        created_at: item.created_at || '',
        likes: item.favorites || 0,
        retweets: item.retweets || 0,
        replies: item.replies || 0,
        views: String(item.views || '0'),
      });
    }

    context.log(`Successfully scraped ${tweets.length} tweets`);

    // Save results to local JSON file
    try {
      const outputPath = path.join(__dirname, '..', '..', 'scraped_tweets.json');
      await fs.writeFile(
        outputPath,
        JSON.stringify(tweets, null, 2),
        'utf-8'
      );
      context.log(`Saved ${tweets.length} tweets to ${outputPath}`);
    } catch (error) {
      context.warn(`Failed to save tweets to file: ${error}`);
    }

    const successResponse: ScrapeResponse = {
      success: true,
      count: tweets.length,
      tweets: tweets,
    };

    return {
      status: 200,
      jsonBody: successResponse,
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      
      if (axiosError.code === 'ECONNABORTED' || axiosError.message.includes('timeout')) {
        context.error('Apify request timed out');
        const errorResponse: ErrorResponse = {
          error: 'Request timed out after 5 minutes',
        };
        return {
          status: 504,
          jsonBody: errorResponse,
        };
      }

      context.error(`Apify request failed: ${axiosError.message}`);
      const errorResponse: ErrorResponse = {
        error: `Scraper failed: ${axiosError.message}`,
      };
      return {
        status: 500,
        jsonBody: errorResponse,
      };
    }

    context.error(`Unexpected error: ${error}`);
    const errorResponse: ErrorResponse = {
      error: `Unexpected error: ${error}`,
    };
    return {
      status: 500,
      jsonBody: errorResponse,
    };
  }
}

app.http('scrape_twitter', {
  methods: ['POST'],
  authLevel: 'function',
  handler: scrapeTwitter,
});


