import { try_catch } from '~/app/api/agents/try_catch';
import { AzureOpenAI } from "openai";
import type { CreateEmbeddingResponse } from "openai/resources/embeddings";

export async function get_embeddings(input_text: string): Promise<CreateEmbeddingResponse> {
	const AZURE_OPENAI_API_KEY = process.env.AZURE_OPENAI_API_KEY ?? '5t0QSorhSr9ExriYXKop8ujE8Q6DRw3y7WVdnHcr7pyUE1iSuLL4JQQJ99BEACfhMk5XJ3w3AAABACOGmiPq';

	// Configure Azure OpenAI client (wrapped in try-catch for sync errors)
	let client: AzureOpenAI;
	try {
		client = new AzureOpenAI({
			endpoint: "https://alex-test-1112.openai.azure.com/",
			apiKey: AZURE_OPENAI_API_KEY,
			deployment: "text-embedding-3-large",
			apiVersion: "2023-05-15"
		});
	} catch (error) {
		throw new Error(`Failed to initialize Azure OpenAI client: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}

	const embeddings_result = await try_catch(
		client.embeddings.create({
			input: [input_text],
			model: "text-embedding-3-large"
		}) as Promise<CreateEmbeddingResponse>
	);

	if (embeddings_result.error !== null) {
		throw new Error(`Failed to generate embeddings: ${embeddings_result.error.message}`);
	}

	return embeddings_result.data;
}