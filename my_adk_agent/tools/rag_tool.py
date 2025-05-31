from google.adk.tools import FunctionTool

mock_document_store = {
    "adk_intro": "ADK (Agent Development Kit) 是一个用于开发和部署 AI 智能体的灵活模块化框架。",
    "adk_features": "ADK 的关键特性包括灵活编排、多智能体架构、丰富的工具生态系统和可部署性。",
    "python_basics": "Python 是一种解释型、高级、通用型编程语言。Python 的设计哲学强调代码的可读性，其显著的特点是代码块的缩进。"
}

def retrieve_from_knowledge_base(query: str, top_k: int = 1) -> str:
    """
    根据用户查询从知识库中检索相关信息。
    这是一个模拟实现，实际应用中会调用真正的 RAG 系统。

    :param query:用户的查询字符串。
    :param top_k: 返回最相关的文档数量。
    :return: 检索到的信息，或未找到信息的提示。
    """
    print(f"[RAG Tool] 接收到查询: {query}, top_k: {top_k}")

    results = []
    query_words = set(query.lower().split())

    for key, doc in mock_document_store.items():
        doc_words = set(doc.lower().split())
        common_words = query_words.intersection(doc_words)
        if common_words:
            results.append({"doc": doc, "score": len(common_words), "key": key})

    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        return f"未能在知识库中找到与 '{query}' 相关的信息。"

    final_docs = [res["doc"] for res in results[:top_k]]

    if not final_docs:
        return f"未能基于查询 '{query}' 提取到有效文档 (top_k={top_k})。"

    return "\n\n".join(final_docs) # 注意这里从

改为 \n\n

rag_tool = FunctionTool(
    func=retrieve_from_knowledge_base,
    name="RetrieveFromKnowledgeBase",
    description="根据用户查询从内部知识库或文档中检索相关信息。用于回答基于特定文档的问题。"
)

if __name__ == '__main__':
    query1 = "什么是 ADK？"
    query2 = "宇宙的起源"

    print(f"测试查询1: '{query1}'")
    response1 = retrieve_from_knowledge_base(query1, top_k=1)
    print(f"响应1:\n{response1}\n") # 注意这里

    print(f"测试查询2 (无相关信息): '{query2}'")
    response2 = retrieve_from_knowledge_base(query2)
    print(f"响应2:\n{response2}\n") # 注意这里
