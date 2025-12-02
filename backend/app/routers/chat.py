from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent.brain import get_agent

router = APIRouter()

agent = get_agent()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "1"

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Configuration for Memory (Thread persistence)
        config = {"configurable": {"thread_id": request.session_id}}
        
        # 2. Input Format
        # LangGraph agents expect a list of messages
        input_payload = {
            "messages": [
                {"role": "user", "content": request.message}
            ]
        }
        
        # 3. Invoke the Agent
        result = agent.invoke(input_payload, config=config)
        
        # 4. Extract the Final Response
        last_message = result["messages"][-1]
        response_content = last_message.content

        # Handle list-based content (Google Style)
        if isinstance(response_content, list):
            response_content = "".join(
                block["text"] for block in response_content 
                if isinstance(block, dict) and block.get("type") == "text"
            )
        
        return {
            "response": response_content,
        }
    except Exception as e:
        print(f"Agent Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))