import { type NextRequest, NextResponse } from 'next/server';
import { handle_post } from './handle_post';
import { processedTweetsSchema } from '~/server/db/schema';
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
		processedTweetsSchema,
		(input) => api.twitter.create(input),
	);
}