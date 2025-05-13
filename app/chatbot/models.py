from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel

class CreateAssistant(BaseModel):
    name: str = None
    instructions: str = None
    model:str  = 'gpt-3.5-turbo'

class CreateUserThread(BaseModel):
    name: str = None   

class MessageThread(BaseModel):
    mes: str = ""

class MessageChatAPI(BaseModel):
    mes: str
    thread_id: str