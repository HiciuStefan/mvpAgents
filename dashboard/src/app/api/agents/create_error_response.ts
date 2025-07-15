import { type NextRequest, NextResponse } from 'next/server';
import { ZodError } from 'zod';
import { TRPCError } from '@trpc/server';
import type { Result } from '~/app/api/agents/try_catch';


const KEYS: Record<agent_type, string>= {
	twitter: 'be380bdf-5c16-4f9c-9473-589cee52d7a3',
	email: 'd0360bf8-28b6-484d-9e17-f34bacf27d6f',
	website: 'c5623212-a89d-4ad3-81fe-c000f70f27de'
}


class AppError extends Error
{
	statusCode: number;

	constructor(statusCode: number, message: string)
	{
		super(message);
		this.statusCode = statusCode;
		Error.captureStackTrace(this, this.constructor);
	}
}


const TRPC_TO_HTTP_STATUS: Record<string, number> = {
	BAD_REQUEST: 400,
	NOT_FOUND: 404,
	CONFLICT: 409,
	INTERNAL_SERVER_ERROR: 500, // Default fallback
};


export function create_error_response(error: unknown)
{
	if (error instanceof ZodError) {
		return NextResponse.json({
			success: false,
			error: 'Validation Error',
			details: error.errors.map((e) => ({
				field: e.path.join('.'),
				message: e.message,
			})),
		}, {
			status: 400
		});
	}

	if (error instanceof TRPCError)
	{
		return NextResponse.json({
			success: false,
			error: error.message,
		}, {
			status: TRPC_TO_HTTP_STATUS[error.code] ?? 500
		});
	}

	if (error instanceof AppError)
	{
		return NextResponse.json({
			success: false,
			error: error.message,
		}, {
			status: error.statusCode
		});
	}

	return NextResponse.json({
		success: false,
		error: 'Internal Server Error',
		details: process.env.NODE_ENV === 'development' ? (error as Error).message : undefined,
	}, {
		status: 500
	});
};



export type agent_type = 'twitter' | 'email' | 'website';

// Validate API key against a specific KEYS object
export function validate_api_key(req: NextRequest, agent: agent_type): Result<void, AppError>
{
	const apiKey = req.headers.get('X-API-Key');
	if (!apiKey)
	{
	  	return {
			data: null,
			error: new AppError(401, 'API key is missing')
		};
	}

	if (KEYS[agent] !== apiKey)
	{
	  	return {
			data: null,
			error: new AppError(401, 'Invalid API key')
		};
	}


	return {
		data: undefined,
		error: null
	};
}

// Validate API key against any key in the KEYS object (agent-agnostic)
export function validate_any_api_key(req: NextRequest): Result<void, AppError>
{
	const apiKey = req.headers.get('X-API-Key');
	if (!apiKey)
	{
	  	return {
			data: null,
			error: new AppError(401, 'API key is missing')
		};
	}

	const validKeys = Object.values(KEYS);
	if (!validKeys.includes(apiKey))
	{
	  	return {
			data: null,
			error: new AppError(401, 'Invalid API key')
		};
	}

	return {
		data: undefined,
		error: null
	};
}