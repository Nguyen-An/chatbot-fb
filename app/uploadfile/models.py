from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

class ChatbotData(Base):
    __tablename__ = 'chatbot_data'

    id = Column(Integer, primary_key=True, index=True)  # Cột id, khóa chính
    file_name = Column(String(255))  # Tên file, độ dài tối đa 255 ký tự
    describe = Column(String(1000))  # Mô tả, độ dài tối đa 1000 ký tự
    file_path = Column(String(255))  # Đường dẫn file, độ dài tối đa 255 ký tự
    file_path_s3 = Column(String(255))  # Đường dẫn S3, độ dài tối đa 255 ký tự
    key = Column(String(255))  # Khóa, độ dài tối đa 255 ký tự
    aifile_id = Column(String(255))  # ID của file trong hệ thống AI, độ dài tối đa 255 ký tự
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)

class ChatbotDataCreate(BaseModel):
    file_name: str
    describe: str
    file_path: str
    file_path_s3: str
    key: str