import type z from 'zod';
import { type NextRequest, NextResponse } from 'next/server';
import { try_catch, type Result } from '~/lib/try_catch';
import {
  create_error_response,
  validate_api_key,
  type agent_type,
} from './create_error_response';

// Abstract DELETE handler utility
export async function handle_delete_by_id<TInput, TOutput>(
  req: NextRequest,
  agent: agent_type,
  params: TInput,
  schema: z.ZodSchema<TInput>,
  mutation: (input: TInput) => Promise<TOutput>
): Promise<NextResponse> {
  // Validate API key
  const api_key_result = validate_api_key(req, agent);
  if (api_key_result.error !== null)
    return create_error_response(api_key_result.error);

  // Get and validate input data
  const input_result = get_input_data(params, schema);
  if (input_result.error !== null)
    return create_error_response(input_result.error);

  // Run mutation
  const mutation_result = await try_catch(mutation(input_result.data));
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

// Function to get input data from query parameters, with fallback to default and validation
function get_input_data<TInput>(
  params: TInput,
  schema: z.ZodSchema<TInput>
): Result<TInput, Error> {
  // Validate input using provided schema
  const zod_validation = schema.safeParse(params);
  if (zod_validation.success === false) {
    return {
      error: zod_validation.error,
      data: null,
    };
  }

  return {
    error: null,
    data: zod_validation.data,
  };
}
