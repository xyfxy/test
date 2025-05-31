import unittest
from my_adk_agent.tools.rag_tool import retrieve_from_knowledge_base, mock_document_store

class TestRagTool(unittest.TestCase):

    def test_retrieve_exact_match(self):
        query = "什么是 ADK？"
        expected_doc = mock_document_store["adk_intro"]
        result = retrieve_from_knowledge_base(query, top_k=1)
        self.assertEqual(result, expected_doc)

    def test_retrieve_partial_match_features(self):
        query = "ADK 有哪些特性"
        expected_doc = mock_document_store["adk_features"]
        result = retrieve_from_knowledge_base(query, top_k=1)
        self.assertEqual(result, expected_doc)

    def test_retrieve_multiple_results(self):
        query = "ADK"
        results = retrieve_from_knowledge_base(query, top_k=2)
        self.assertIn(mock_document_store["adk_intro"], results)
        self.assertIn(mock_document_store["adk_features"], results)
        self.assertIn("\n\n", results)

    def test_retrieve_no_match(self):
        query = "宇宙的起源是什么？"
        result = retrieve_from_knowledge_base(query, top_k=1)
        self.assertEqual(result, f"未能在知识库中找到与 '{query}' 相关的信息。")

    def test_retrieve_top_k_greater_than_matches(self):
        query = "Python"
        expected_doc = mock_document_store["python_basics"]
        result = retrieve_from_knowledge_base(query, top_k=5)
        self.assertEqual(result, expected_doc)

    def test_retrieve_empty_query(self):
        query = ""
        result = retrieve_from_knowledge_base(query, top_k=1)
        self.assertEqual(result, f"未能在知识库中找到与 '{query}' 相关的信息。")

if __name__ == '__main__':
    unittest.main()
