import unittest
from unittest.mock import patch, MagicMock
import os
import requests
from rag_retriever import get_rag_context

class TestRagRetriever(unittest.TestCase):

    def setUp(self):
        os.environ['IS_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['IS_TESTING']

    @patch('rag_retriever.requests.get')
    def test_get_rag_context_success(self, mock_get):
        os.environ['RAG_API_URL'] = 'http://mock-rag-api.com'
        os.environ['RAG_API_KEY'] = 'mock_key'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"context": "This is a mock RAG context."}
        mock_get.return_value = mock_response

        content = "test query"
        context = get_rag_context(content)

        mock_get.assert_called_once_with(
            'http://mock-rag-api.com',
            headers={"X-API-key": "mock_key", "Content-Type": "application/json"},
            params={"text": content}
        )
        self.assertEqual(context, "This is a mock RAG context.")

    def test_get_rag_context_missing_env_vars(self):
        if 'RAG_API_URL' in os.environ: del os.environ['RAG_API_URL']
        if 'RAG_API_KEY' in os.environ: del os.environ['RAG_API_KEY']

        content = "test query"
        context = get_rag_context(content)
        self.assertEqual(context, "")

    @patch('rag_retriever.requests.get')
    def test_get_rag_context_request_exception(self, mock_get):
        os.environ['RAG_API_URL'] = 'http://mock-rag-api.com'
        os.environ['RAG_API_KEY'] = 'mock_key'

        mock_get.side_effect = requests.exceptions.RequestException("Test exception")

        content = "test query"
        context = get_rag_context(content)

        self.assertEqual(context, "")

if __name__ == '__main__':
    unittest.main()
