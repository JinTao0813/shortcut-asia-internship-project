from langchain.tools import BaseTool
from typing import Optional
from services.rag_service import RAGService
from dependencies import llm

# -------------------- Initialize RAG Service --------------------
rag_service = RAGService(llm)

# -------------------- RAG LangChain Tool --------------------
class ZUSRAGTool(BaseTool):
    name: str = "zus_rag_search"
    description: str = (
        "Search ZUS Coffee's internal database for information about products (drinkware, tumblers, cups), "
        "food items (meals, pastries, food menu), drinks (beverages, coffee, tea, drink menu), "
        "outlets (locations, addresses, store info), prices, categories, and other internal data. "
        "This tool uses embeddings to find the most relevant and accurate information. "
        "Input: A natural language question about ZUS Coffee products, food, drinks, or outlets."
    )

    def _run(self, query: str) -> str:
        """
        Synchronous run method for LangChain.
        Searches internal database using RAG with embeddings.
        """
        result = rag_service.search_and_summarize(query=query, top_k=5)
        return result["summary"]

    async def _arun(self, query: str) -> str:
        """
        Asynchronous run method for LangChain.
        Searches internal database using RAG with embeddings.
        """
        result = rag_service.search_and_summarize(query=query, top_k=5)
        return result["summary"]

# -------------------- Instantiate the tool --------------------
zus_rag_tool = ZUSRAGTool()
