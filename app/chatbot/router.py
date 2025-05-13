from fastapi import APIRouter,Request, Depends, Response, status, HTTPException,BackgroundTasks

from sqlalchemy.orm import Session
from .models import *
from ..database import get_db
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.common.responses_msg import *
from openai import AsyncOpenAI
import os
from .service import ChatbotService

chat = ChatbotService()
router_chat_bot = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)

open_api_key =os.getenv('OPENAI_KEY','')
assistant_id = os.getenv('ASSISTANT_ID','')
vector_store_id = os.getenv('VECTOR_STORE_ID','')
@router_chat_bot.get("")
async def get_list_vector_store(request:Request, db: Session = Depends(get_db)):
    try:
        vector_stores = await AsyncOpenAI(api_key=open_api_key).beta.vector_stores.list()
        return vector_stores 
    except Exception as e:
        print(e)
        return "err"
    
@router_chat_bot.post("")
async def create_vector_store(request:Request, db: Session = Depends(get_db)):
    try:
        vector_store = await AsyncOpenAI(api_key=open_api_key).beta.vector_stores.create(name="vector_store default") 
        return vector_store 
    except Exception as e:
        print(e)
        return "err"
    
@router_chat_bot.post("/messenger")
async def messenger(request:Request, messageChatAPI : MessageChatAPI, db: Session = Depends(get_db)):
    try:
        mess = await chat.chat_messenger_api(messageChatAPI)
        return mess
    except Exception as e:
        print(e)
        return "err"

@router_chat_bot.get("/assistant")
async def get_list_assistant(request:Request, db: Session = Depends(get_db)):
    try:
        assistants = await AsyncOpenAI(api_key=open_api_key).beta.assistants.list() 
        return assistants 
    except Exception as e:
        print(e)
        return "err"
    
@router_chat_bot.post("/assistant")
async def create_assistant(request:Request, createAssistant: CreateAssistant, db: Session = Depends(get_db)):
    try:
        openai_assistant = await AsyncOpenAI(api_key=open_api_key).beta.assistants.create(
            name=createAssistant.name,
            instructions=createAssistant.instructions,
            model=createAssistant.model,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
            )
        return openai_assistant
    except Exception as e:
        print(e)
        return "err"
    
@router_chat_bot.post("/assistant/thread")
async def create_thread(request:Request, db: Session = Depends(get_db)):
    try:
        thread = await AsyncOpenAI(api_key=open_api_key).beta.threads.create()    
        return thread
    except Exception as e:
        print(e)
        return "err"
    
