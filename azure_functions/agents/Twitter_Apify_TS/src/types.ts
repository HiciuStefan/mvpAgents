export interface ScrapeTwitterRequest {
  username?: string;
  max_posts?: number;
  search_type?: string;
}

export interface ApifyActorInput {
  username: string;
  max_posts: number;
  search_type: string;
}

export interface ApifyAuthor {
  screen_name?: string;
  name?: string;
}

export interface ApifyTweetItem {
  demo?: boolean;
  tweet_id?: string;
  text?: string;
  author?: ApifyAuthor;
  created_at?: string;
  favorites?: number;
  retweets?: number;
  replies?: number;
  views?: string | number;
}

export interface Tweet {
  tweet_id: string;
  url: string;
  text: string;
  author: string;
  created_at: string;
  likes: number;
  retweets: number;
  replies: number;
  views: string;
}

export interface ScrapeResponse {
  success: boolean;
  count: number;
  tweets: Tweet[];
}

export interface ErrorResponse {
  error: string;
}


