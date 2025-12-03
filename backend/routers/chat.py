from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from schemas import ChatRequest, ChatResponse, ChatMessage
from agent.brain import create_agent_instance
from dependencies import get_llm

router = APIRouter()

# In-memory session storage (use Redis in production)
chat_sessions: Dict[str, List[ChatMessage]] = {}

# ==================== Chat with Agent ====================
@router.post("/", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, llm=Depends(get_llm)):
    """
    Chat endpoint that uses a ReAct agent with RAG tool.
    
    Flow:
    1. User sends a message
    2. Agent receives the message and decides whether to use the RAG tool
    3. RAG tool searches FAISS embeddings for accurate internal data
    4. Agent formats and returns the response
    
    This ensures all product/outlet queries use embeddings, not LLM general knowledge.
    """
    try:
        session_id = request.session_id or "default"
        
        # Get or create session history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Add user message to history
        user_message = ChatMessage(role="user", content=request.message)
        chat_sessions[session_id].append(user_message)
        
        # Create agent with LLM
        agent = create_agent_instance(llm)
        
        # Prepare messages for agent (convert to LangChain message format)
        from langchain_core.messages import HumanMessage, AIMessage
        
        messages = []
        # Include all chat history including current message
        for msg in chat_sessions[session_id]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # Invoke agent with messages format - it will automatically call the RAG tool when needed
        result = agent.invoke({"messages": messages})
        
        # Extract response from agent result - get last message content
        result_messages = result.get("messages", [])
        if result_messages:
            last_message = result_messages[-1]
            if hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = str(last_message)
        else:
            response_text = "I'm sorry, I couldn't process that request."
        
        # Handle list content format (e.g., Claude)
        if isinstance(response_text, list):
            text_parts = []
            for item in response_text:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif isinstance(item, str):
                    text_parts.append(item)
            response_text = ' '.join(text_parts).strip()
        else:
            response_text = str(response_text)
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response_text)
        chat_sessions[session_id].append(assistant_message)
        
        return ChatResponse(response=response_text, session_id=session_id)
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# ==================== Get Chat History ====================
@router.get("/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a session.
    """
    if session_id not in chat_sessions:
        return []
    return chat_sessions[session_id]

# ==================== Clear Chat History ====================
@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a session.
    """
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {"message": f"Chat history for session '{session_id}' cleared."}