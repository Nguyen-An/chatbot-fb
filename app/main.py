from fastapi import Depends, FastAPI,Request,Cookie, HTTPException, status
from contextlib import contextmanager,asynccontextmanager
from app.database import get_db, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.uploadfile.router import router_uploadfile
from app.chatbot.router import router_chat_bot
from app.common.responses_msg import *
from fastapi.responses import JSONResponse
from .common.api_const import paths
import socketio
from app.chatbot.service import ChatbotService
import asyncio

@asynccontextmanager
async def lifespan_context(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan_context)

get_db_manager = contextmanager(get_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://datn-mquickb-fe-v2.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_uploadfile)
app.include_router(router_chat_bot)
load_dotenv()
chat = ChatbotService()

sio  = socketio.AsyncServer(async_mode='asgi',cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio)

app.mount("/", socket_app)

@sio.on('connect')
async def connect(sid, environ):    
    with get_db_manager() as db:             
        await chat.set_up_handle(db,sio,sid) 
    await sio.emit('connect_ok', "Message from server to "+sid,to=sid)

@sio.on('disconnect')
async def disconnect(sid):
    pass

@sio.on('message')
async def message(sid, data):      
    with get_db_manager() as db:             
        await chat.chat_handler(data,db,sio,sid)
