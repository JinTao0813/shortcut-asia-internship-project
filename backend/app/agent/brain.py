from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from dependencies import llm
from app.agent.tools import tools

def get_agent():
    memory = InMemorySaver()

    system_message = (
        "You are a helpful assistant for ZUS Coffee. "
        "You have access to tools for searching products, finding outlets, and doing calculations. "
        "Always use the appropriate tool for the user's question. "
        "If the user follows up on a previous question, use the chat history context."
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_message,
        checkpointer=memory
    )
    
    return agent 