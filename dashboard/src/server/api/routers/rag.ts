import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { rag_get_schema, rag_post_schema, rag_delete_schema } from '~/server/db/schema';
import { try_catch } from '~/app/api/agents/try_catch';
import { get_embeddings } from '~/server/api/utils/get_embeddings';
import { upload_embeddings } from '~/server/api/utils/upload_embeddings';
import { SearchClient, AzureKeyCredential } from "@azure/search-documents";

interface DeleteDocument {
	[key: string]: unknown;
	"@search.action": "delete";
}

const endpoint = "https://ais-search-swc.search.windows.net";
const apiKey = process.env.RAG_API_KEY ?? '';
const indexName = "index1751888498617";

export const rag_router = createTRPCRouter({
	get: publicProcedure
		.input(rag_get_schema)
		.query(async ({ input }) => {
			const client = new SearchClient(endpoint, indexName, new AzureKeyCredential(apiKey));

			// For now, implement simple text-based search
			// TODO: Implement proper vector search when SDK supports it
			const search_result = await try_catch(client.search("*", {
				vectorSearchOptions: {
					queries: [{
						kind: "text",
						text: input.text,
						fields: ["vector"],
						kNearestNeighborsCount: 10,
					}],
				},
			}));


			if (search_result.error !== null) {
				throw new Error(`Failed to search documents: ${search_result.error.message}`);
			}

			const results = search_result.data;
			const documents = [];

			for await (const result of results.results) {
				const doc = result.document as Record<string, unknown>;
				documents.push({
					id: doc.id,
					content: doc.content,
					score: result.score
				});
			}

			return {
				message: `Found ${documents.length} documents for: ${input.text}`,
				result: "RAG search completed",
				documents: documents,
				query: input.text
			};
		}),

	create: publicProcedure
		.input(rag_post_schema)
		.mutation(async ({ input }) => {
			// Step 1: Get embeddings for the input text
			const embeddings_result = await try_catch(get_embeddings(input.input));

			if (embeddings_result.error !== null) {
				throw new Error(`Failed to process embeddings: ${embeddings_result.error.message}`);
			}

			const embeddings_response = embeddings_result.data;

			// Step 2: Upload embeddings to Azure Search
			const upload_result = await try_catch(upload_embeddings(embeddings_response, input.input));

			if (upload_result.error !== null) {
				throw new Error(`Failed to upload embeddings: ${upload_result.error.message}`);
			}

			const upload_response = upload_result.data;

			return {
				message: `Successfully processed and uploaded embeddings for: ${input.input}`,
				result: "Embeddings generated and uploaded",
				upload: upload_response,
				usage: embeddings_response.usage
			};
		}),

	delete: publicProcedure
		.input(rag_delete_schema)
		.mutation(async () => {
			const keyField = "ID"; // Changed back to lowercase "id" to match the uploaded documents

			const client = new SearchClient(endpoint, indexName, new AzureKeyCredential(apiKey));

			console.log("Fetching all document keys...");

			const deleteBatch: DeleteDocument[] = [];

			const search_result = await try_catch(client.search("*", { select: [keyField], top: 1000 }));

			if (search_result.error !== null) {
				throw new Error(`Failed to search documents: ${search_result.error.message}`);
			}

			const results = search_result.data;

			for await (const result of results.results) {
				const doc = result.document as Record<string, unknown>;
				if (doc[keyField]) {
					deleteBatch.push({
						[keyField]: doc[keyField],
						"@search.action": "delete"
					});
				}
			}

			console.log(`Found ${deleteBatch.length} documents. Deleting in batches...`);

			if (deleteBatch.length === 0) {
				return {
					message: "No documents found to delete",
					result: "No action taken",
					deleted_count: 0
				};
			}

			const batchSize = 1000; // Azure Search limit per batch
			let deletedCount = 0;

			for (let i = 0; i < deleteBatch.length; i += batchSize) {
				const batch = deleteBatch.slice(i, i + batchSize);
				const delete_result = await try_catch(client.uploadDocuments(batch));

				if (delete_result.error !== null) {
					throw new Error(`Failed to delete batch ${i / batchSize + 1}: ${delete_result.error.message}`);
				}

				deletedCount += batch.length;
				console.log(`Deleted batch ${i / batchSize + 1}`);
			}

			console.log("✅ All documents deleted.");

			return {
				message: `Successfully deleted ${deletedCount} documents from Azure Search index`,
				result: "All documents deleted",
				deleted_count: deletedCount
			};
		}),
});
