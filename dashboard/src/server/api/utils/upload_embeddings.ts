import { try_catch } from '~/app/api/agents/try_catch';
import { randomUUID } from 'crypto';
import type { CreateEmbeddingResponse } from "openai/resources/embeddings";

interface SearchUploadDocument {
	"@search.action": "upload";
	"id": string;
	"title": string;
	"content": string;
	"vector": number[];
}

interface SearchUploadRequest {
	value: SearchUploadDocument[];
}

interface AzureSearchResponse {
	"@odata.context": string;
	value: Array<{
		key: string;
		status: boolean;
		errorMessage?: string;
		statusCode: number;
	}>;
}

export async function upload_embeddings(embeddings_response: CreateEmbeddingResponse, input: string): Promise<AzureSearchResponse | null> {
	const AZURE_SEARCH_API_KEY = process.env.AZURE_SEARCH_API_KEY ?? 'eqbSD8mEmAhsQvTanXL7CrgBNjD9As8OG3tyNoGiY0AzSeDQqxRP';

	// Construct the search URL
	const search_url = 'https://ais-search-swc.search.windows.net/indexes/index1751888498617/docs/index?api-version=2024-07-01';

	if (embeddings_response.data[0] === undefined)
	{
		throw new Error('No embeddings data found');
	}

	const embedding = embeddings_response.data[0].embedding;

	// Transform embeddings data into the required format
	const document: SearchUploadDocument = {
		"@search.action": "upload",
		"id": randomUUID(), // Generate UUID v4
		"title": "no_title",
		"content": input,
		"vector": embedding
	};

	const request_body: SearchUploadRequest = {
		value: [document]
	};

	// console.log(request_body);
	// return null;

	const upload_result = await try_catch(fetch(search_url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'api-key': AZURE_SEARCH_API_KEY,
		},
		body: JSON.stringify(request_body)
	}));

	if (upload_result.error !== null) {
		throw new Error(`Failed to call Azure Search API: ${upload_result.error.message}`);
	}

	const response = upload_result.data;
	if (!response.ok) {
		throw new Error(`Azure Search API error: ${response.status} ${response.statusText}`);
	}

	const json_result = await try_catch(response.json());
	if (json_result.error !== null) {
		throw new Error(`Failed to parse Azure Search response: ${json_result.error.message}`);
	}

	return json_result.data as AzureSearchResponse;
}