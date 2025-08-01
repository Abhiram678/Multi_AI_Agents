from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
from app.core.ai_agent import get_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

app = FastAPI(title="MULTI AI AGENT")

class RequestState(BaseModel):
    model_name:str
    system_prompt:str
    messages:List[str]
    allow_search: bool

# ...existing code...

@app.post("/chat")
def chat_endpoint(request: RequestState):
    logger.info(f"Received request for model: {request.model_name}")

    # Validate model name
    if request.model_name not in settings.ALLOWED_MODEL_NAMES:
        logger.warning("Invalid model name")
        raise HTTPException(status_code=400, detail="Invalid model name")

    # Enforce domain-specific constraints
    if "medical" not in request.system_prompt.lower():
        logger.warning("System prompt is outside the allowed domain")
        raise HTTPException(status_code=400, detail="System prompt must be related to the medical domain")

    try:
        response = get_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt
        )

        logger.info(f"Successfully got response from AI Agent {request.model_name}")

        return {"response": response}

    except Exception as e:
        logger.error("Some error occurred during response generation")
        raise HTTPException(
            status_code=500,
            detail=str(CustomException("Failed to get AI response", error_detail=e))
        )


