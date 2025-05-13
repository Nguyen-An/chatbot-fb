from fastapi import APIRouter,Request, Depends, Response

from .service import UploadFileService
from fastapi import UploadFile
from typing import List
from ..database import get_db
from sqlalchemy.orm import Session
from .models import *
from fastapi.responses import JSONResponse
from ..common.responses_msg import *
from ..common.responses import *

router_uploadfile = APIRouter(
    prefix="/uploadfile",
    tags=["uploadfile"],
    responses={404: {"description": "Not found"}},
)

UploadFileService
@router_uploadfile.post("/upload/avatar")
async def upload_avatar(request:Request,file: UploadFile, db: Session = Depends(get_db)):  
    user_info = request.state.info_user
    try:
        key =  await UploadFileService.upload_avatar_to_s3(user_info,file,db)        
        return key
    except Exception as e:        
        return JSONResponse(
            status_code=e.status_code,
            content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code"))
        ) 
    
@router_uploadfile.post("/upload/file-s3")
async def upload_file_s3(request:Request,file: UploadFile, db: Session = Depends(get_db)):  
    user_info = request.state.info_user
    try:
        key =  await UploadFileService.upload_file_to_s3(user_info,file,db)        
        return key
    except Exception as e:        
        return JSONResponse(
            status_code=e.status_code,
            content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code"))
        ) 
    
@router_uploadfile.post("/upload/file")
async def upload_file_s3(request:Request,chatbotDataCreate: ChatbotDataCreate, db: Session = Depends(get_db)):  
    user_info = request.state.info_user
    try:
        key =  await UploadFileService.upload_file_chatbot(db, user_info, chatbotDataCreate)        
        return key
    except Exception as e:
        print("err: ", e)
        return JSONResponse(
            status_code=e.status_code,
            content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code"))
        ) 
    

@router_uploadfile.get("/files")
async def get_files (request:Request, page:int=1, page_size:int=20, key_word:str="", db: Session = Depends(get_db)):
    try:
        t = await UploadFileService.get_files_service(db, page, page_size, key_word)
        return t
    except Exception as e:
        return JSONResponse(
            status_code=e.status_code,
            content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code"))
        )  
    
@router_uploadfile.delete("/delete-file/{key}", responses=common_responses)
async def delete_file(request:Request,key: str, db: Session = Depends(get_db)):
    return await UploadFileService.delete_file(key, db)