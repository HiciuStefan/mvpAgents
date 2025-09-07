import type z from 'zod';
import { type NextRequest, NextResponse } from 'next/server';
import { try_catch } from '~/lib/try_catch';
import {
  create_error_response,
  validate_any_api_key,
} from '~/app/api/agents/create_error_response';

// RAG DELETE handler utility - simplified without agent validation
export async function handle_delete<TInput, TOutput>(
  req: NextRequest,
  schema: z.ZodSchema<TInput>,
  mutation: (input: TInput) => Promise<TOutput>
): Promise<NextResponse> {
  // Validate API key
  const api_key_result = validate_any_api_key(req);
  if (api_key_result.error !== null)
    return create_error_response(api_key_result.error);

  // Parse JSON (if body exists)
  let parsed_input: unknown = {};
  const content_type = req.headers.get('content-type');

  if (content_type?.includes('application/json')) {
    const JSON_result = await try_catch(req.json());
    if (JSON_result.error !== null) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid JSON format',
          details: JSON_result.error.message,
        },
        {
          status: 400,
        }
      );
    }
    parsed_input = JSON_result.data;
  }

  // Validate input using provided schema
  const zod_validation = schema.safeParse(parsed_input);
  if (zod_validation.success === false)
    return create_error_response(zod_validation.error);

  // Run mutation
  const mutation_result = await try_catch(mutation(zod_validation.data));
  if (mutation_result.error !== null)
    return create_error_response(mutation_result.error);

  // Return success
  return NextResponse.json(
    {
      success: true,
      data: mutation_result.data,
    },
    {
      status: 200,
    }
  );
}
