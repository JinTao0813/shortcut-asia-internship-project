from langchain.agents import create_agent
from dependencies import llm
from agent.tools import zus_rag_tool


def create_agent_instance(llm_instance=None):
    """
    Create a modern LangChain agent using langchain.agents.create_agent().
    Handles RAG queries for ZUS Coffee using the zus_rag_tool.
    """

    # Select LLM model
    model = llm_instance if llm_instance else llm

    # System prompt as string (not SystemMessage object)
    system_prompt = (
        "You are a helpful assistant for ZUS Coffee internal operations.\n\n"
        "CRITICAL: You MUST use the 'zus_rag_search' tool for ANY question about:\n"
        "- Products, drinkware, tumblers, cups, or merchandise\n"
        "- Outlets, stores, locations, or addresses\n"
        "- Prices, categories, or product details\n"
        "- Store hours, contact info, or outlet information\n\n"
        "DO NOT answer from memory or general knowledge. ALWAYS call the tool first.\n"
        "The tool searches our internal database with embeddings for accurate, up-to-date information.\n\n"
        "After getting tool results, format them nicely for the user."
    )

    tools = [zus_rag_tool]

    # Create agent with system_prompt as string
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )

    return agent
