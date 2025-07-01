import { type NextRequest } from 'next/server';
import { api } from "~/trpc/server";
import { processed_tweets_schema, processed_GET_schema, processed_DELETE_schema } from '~/server/db/schema';
import { handle_get } from '~/app/api/agents/handle_get';
import { handle_post } from '~/app/api/agents/handle_post';
import { handle_delete } from '~/app/api/agents/handle_delete';



export async function GET(req: NextRequest)
{
	return handle_get(
		req,
		'twitter',
		processed_GET_schema,
		(input) => api.twitter.getLatest(input),
	);
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


export async function DELETE(req: NextRequest)
{
	return handle_delete(
		req,
		'twitter',
		processed_DELETE_schema,
		(input) => api.twitter.delete_all(input),
	);
}