import { type NextRequest } from 'next/server';
import { api } from "~/trpc/server";
import { handle_delete_by_id } from '~/app/api/agents/handle_delete_by_id';
import { processed_DELETE_by_id_schema } from '~/server/db/schema';



export async function DELETE(
	req: NextRequest,
	{ params }: { params: Promise<{ id: string }>}
) {
	const { id } = await params;

	return handle_delete_by_id(
		req,
		'email',
		{ id },
		processed_DELETE_by_id_schema,
		(input) => api.email.delete_one(input),
	);
}