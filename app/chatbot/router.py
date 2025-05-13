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
from fastapi.responses import HTMLResponse, PlainTextResponse
import httpx

router_chat_bot = APIRouter(
    prefix="/messaging-webhook",
    tags=["messaging-webhook"],
    responses={404: {"description": "Not found"}},
)

open_api_key =os.getenv('OPENAI_KEY','')
assistant_id = os.getenv('ASSISTANT_ID','')
vector_store_id = os.getenv('VECTOR_STORE_ID','')
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# @router_chat_bot.post("/messenger-xxx")
# async def messenger(request:Request, messageChatAPI : MessageChatAPI, db: Session = Depends(get_db)):
#     try:
#         mess = await ChatbotService.chat_messenger_api(messageChatAPI)
#         return mess
#     except Exception as e:
#         print(e)
#         return "err"
    

@router_chat_bot.get("")
async def get_webhook(request:Request, db: Session = Depends(get_db)):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            return Response(status_code=403)
    return Response(status_code=400)

@router_chat_bot.post("")
async def post_webhook(request: Request):
    print("Webhook triggered")
    body = await request.json()
    print("Request body:", body)

    if body.get("object") == "page":
        for entry in body.get("entry", []):
            messaging = entry.get("messaging", [])
            if not messaging:
                continue

            webhook_event = messaging[0]
            print(webhook_event)

            sender_psid = webhook_event["sender"]["id"]
            print("Sender PSID:", sender_psid)

            if "message" in webhook_event:
                await handle_message(sender_psid, webhook_event["message"])
            elif "postback" in webhook_event:
                await handle_postback(sender_psid, webhook_event["postback"])

        return PlainTextResponse(content="EVENT_RECEIVED", status_code=200)
    else:
        return Response(status_code=404)

# Xử lý message
async def handle_message(sender_psid: str, received_message: dict):
    if "text" in received_message:
        # Trích xuất nội dung text từ received_message
        message_text = received_message["text"]
        
        new_messageChatAPI = MessageChatAPI(
            mes=message_text, 
            thread_id="thread_BY2sCULMTU7sW2C2uAuGbfo7",
        )
        mes = await ChatbotService.chat_messenger_api(new_messageChatAPI)
        print("mes: ", mes)
        response = {
            "text": mes
        }
        await call_send_api(sender_psid, response)

# Xử lý postback (chưa triển khai)
async def handle_postback(sender_psid: str, received_postback: dict):
    pass

# Gửi tin nhắn qua Facebook Send API
async def call_send_api(sender_psid: str, response: dict):
    request_body = {
        "recipient": {"id": sender_psid},
        "message": response
    }

    url = "https://graph.facebook.com/v2.6/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, params=params, json=request_body)
        if r.status_code == 200:
            print("message sent!")
        else:
            print("Unable to send message:", r.text)


# @router_chat_bot.get("")
# async def get_list_vector_store(request:Request, db: Session = Depends(get_db)):
#     try:
#         vector_stores = await AsyncOpenAI(api_key=open_api_key).beta.vector_stores.list()
#         return vector_stores 
#     except Exception as e:
#         print(e)
#         return "err"
    
# @router_chat_bot.post("")
# async def create_vector_store(request:Request, db: Session = Depends(get_db)):
#     try:
#         vector_store = await AsyncOpenAI(api_key=open_api_key).beta.vector_stores.create(name="vector_store default") 
#         return vector_store 
#     except Exception as e:
#         print(e)
#         return "err"
    




# @router_chat_bot.get("/assistant")
# async def get_list_assistant(request:Request, db: Session = Depends(get_db)):
#     try:
#         assistants = await AsyncOpenAI(api_key=open_api_key).beta.assistants.list() 
#         return assistants 
#     except Exception as e:
#         print(e)
#         return "err"
    
# @router_chat_bot.post("/assistant")
# async def create_assistant(request:Request, createAssistant: CreateAssistant, db: Session = Depends(get_db)):
#     try:
#         openai_assistant = await AsyncOpenAI(api_key=open_api_key).beta.assistants.create(
#             name=createAssistant.name,
#             instructions=createAssistant.instructions,
#             model=createAssistant.model,
#             tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
#             )
#         return openai_assistant
#     except Exception as e:
#         print(e)
#         return "err"
    
# @router_chat_bot.post("/assistant/thread")
# async def create_thread(request:Request, db: Session = Depends(get_db)):
#     try:
#         thread = await AsyncOpenAI(api_key=open_api_key).beta.threads.create()    
#         return thread
#     except Exception as e:
#         print(e)
#         return "err"
    
