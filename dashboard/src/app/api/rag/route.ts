import { type NextRequest } from 'next/server';
import { api } from "~/trpc/server";
import { rag_get_schema, rag_post_schema, rag_delete_schema } from '~/server/db/schema';
import { handle_get } from '~/app/api/rag/handle_get';
import { handle_post } from '~/app/api/rag/handle_post';
import { handle_delete } from '~/app/api/rag/handle_delete';

export async function GET(req: NextRequest)
{
	return handle_get(
		req,
		rag_get_schema,
		(input) => api.rag.get(input),
	);
}

export async function POST(req: NextRequest)
{
	return handle_post(
		req,
		rag_post_schema,
		(input) => api.rag.create(input),
	);
}

export async function DELETE(req: NextRequest)
{
	return handle_delete(
		req,
		rag_delete_schema,
		(input) => api.rag.delete(input),
	);
}