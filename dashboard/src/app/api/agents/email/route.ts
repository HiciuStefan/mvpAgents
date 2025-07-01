import { type NextRequest } from 'next/server';
import { api } from "~/trpc/server";
import { processed_DELETE_schema, processed_emails_schema, processed_GET_schema } from '~/server/db/schema';
import { handle_get } from '~/app/api/agents/handle_get';
import { handle_post } from '~/app/api/agents/handle_post';
import { handle_delete } from '~/app/api/agents/handle_delete';



export async function GET(req: NextRequest)
{
	return handle_get(
		req,
		'email',
		processed_GET_schema,
		(input) => api.email.getLatest(input),
	);
}


export async function POST(req: NextRequest)
{
	return handle_post(
		req,
		'email',
		processed_emails_schema,
		(input) => api.email.create(input),
	);
}


export async function DELETE(req: NextRequest)
{
	return handle_delete(
		req,
		'email',
		processed_DELETE_schema,
		(input) => api.email.delete_all(input),
	);
}