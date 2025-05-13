import json
from urllib.request import urlretrieve
from fastapi import UploadFile, HTTPException, Depends, status, Response
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import os
from tempfile import NamedTemporaryFile
import uuid
from sqlalchemy.orm import Session
from .crud import *
from ..common.responses_msg import *
from .models import *
from urllib.parse import quote
from openai import NOT_GIVEN, AsyncOpenAI

open_api_key =os.getenv('OPENAI_KEY','')
vector_store_id = os.getenv('VECTOR_STORE_ID','')

UPLOAD_DIR = Path("app/data/files")
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_FILES_COUNT = 5

# Danh sách các định dạng file hợp lệ
ALLOWED_EXTENSIONS = {
    ".c", ".cs", ".cpp", ".doc", ".docx", ".html",
    ".java", ".json", ".pdf", ".php", ".pptx", ".txt", ".js", '.md'
}

AVATAR_FILES = {
    ".jpg", ".png", ".svg"
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Cấu hình thông tin AWS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID','')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY','')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME','')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME','')

# Khởi tạo client của S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

class UploadFileService:
    async def upload_avatar_to_s3(user_info, file: UploadFile, db: Session):
        # Kiểm tra định dạng file
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in AVATAR_FILES:
            raise HTTPException(status_code=400, detail="FILE_FORMAT_NOT_SUPPORTED")
        
        # Kiểm tra kích thước file
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="FILE_SIZE_EXCEEDED")
        
        # Kiểm tra nếu file rỗng
        if file.size == 0:
            raise HTTPException(status_code=400, detail="FILE_EMPTY")
        
        # Tạo tên file duy nhất
        unique_filename = str(uuid.uuid4()) + file_extension  # Đảm bảo giữ đúng phần mở rộng

        try:
            # Tạo tên file tạm thời
            temp_file = NamedTemporaryFile(delete=False)
            temp_file.write(await file.read())
            temp_file.close()

            # Upload file lên S3 và set quyền công khai
            s3_client.upload_file(
                temp_file.name, 
                S3_BUCKET_NAME, 
                unique_filename,
                ExtraArgs={
                    'ContentType': file.content_type,
                }
            )  

            # Tạo URL công khai cho file đã upload
            file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"

            # Trả về URL và tên file
            return {"filename": unique_filename, "url": file_url}

        except Exception as e:
            print("error: ", e)
            raise HTTPException(status_code=400, detail="UPLOOAD_S3_FAIL")
    
    async def upload_file_to_s3(user_info, file: UploadFile, db: Session):
        # Kiểm tra định dạng file
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="FILE_FORMAT_NOT_SUPPORTED")
        
        # Kiểm tra kích thước file
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="FILE_SIZE_EXCEEDED")
        
        # Kiểm tra nếu file rỗng
        if file.size == 0:
            raise HTTPException(status_code=400, detail="FILE_EMPTY")
        
        # Tạo tên file duy nhất
        unique_filename = str(uuid.uuid4()) + file_extension  # Đảm bảo giữ đúng phần mở rộng

        try:
            # Tạo tên file tạm thời
            temp_file = NamedTemporaryFile(delete=False)
            temp_file.write(await file.read())
            temp_file.close()

            # Upload file lên S3 và set quyền công khai
            s3_client.upload_file(
                temp_file.name, 
                S3_BUCKET_NAME, 
                unique_filename,
                ExtraArgs={
                    'ContentType': file.content_type,
                }
            )  

            # Tạo URL công khai cho file đã upload
            file_url_s3 = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"

            file_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET_NAME, 'Key': unique_filename},
                )
            # Trả về URL và tên file
            return {"filename": unique_filename, "file_url_s3": file_url_s3, "file_url": file_url}

        except Exception as e:
            print("error: ", e)
            raise HTTPException(status_code=400, detail="UPLOOAD_S3_FAIL")
        

    async def upload_file_chatbot(db: Session, user_info, chatbotDataCreate: ChatbotDataCreate):
        file_info = ChatbotData(
                file_name = chatbotDataCreate.file_name,
                describe = chatbotDataCreate.describe,
                file_path = chatbotDataCreate.file_path,
                file_path_s3 = chatbotDataCreate.file_path_s3,
                key = chatbotDataCreate.key,
                aifile_id = ""
                )
        aifile = await UploadFileService.upload_file_to_openai(file_info)

        file_info.aifile_id = aifile.id

        await AsyncOpenAI(api_key=open_api_key).beta.vector_stores.files.create(vector_store_id=vector_store_id, file_id=file_info.aifile_id) 
        file_result = create_file_db(db, file_info)
        return file_result
        
    @staticmethod
    async def upload_file_to_openai(file:ChatbotData):
        folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'\\statics'
        if not os.path.exists(folder):
            os.makedirs(folder)
        path = folder+"\\"+file.file_name
        urlretrieve(file.file_path_s3, path)
        f = open(path, 'rb')        
        message_file = await AsyncOpenAI(api_key=open_api_key).files.create(file=f, purpose="assistants")       
        f.close()                        
        os.remove(path)
        return message_file
    
    async def get_files_service(db: Session, page:int, page_size:int, key_word:str):
        files = get_files_db(db, page, page_size, key_word)
        return files
    
    async def delete_file(key: str, db: Session):
        try:
            # Xóa file từ bucket
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=key)
            except s3_client.exceptions.NoSuchKey:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in S3")

            # Xóa file trong db
            try:
                file = delete_file(db, key)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in database")

            if file.aifile_id:
                async with AsyncOpenAI(api_key=open_api_key) as ai_client:
                    await ai_client.files.delete(file.aifile_id)

            return {"status": "success"}

        except Exception as e:
            print("er: ", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")