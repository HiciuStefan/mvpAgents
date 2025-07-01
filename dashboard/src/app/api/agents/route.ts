import { type NextRequest, NextResponse } from 'next/server';
import { handle_post } from './handle_post';
import { processed_tweets_schema } from '~/server/db/schema';
import { api } from "~/trpc/server";


export async function GET()
{
	return NextResponse.json({});
}


export async function POST(req: NextRequest)
{
	return handle_post(
		req,
		'twitter',
		processed_tweets_schema,
		(input) => api.twitter.create(input),
	);
}