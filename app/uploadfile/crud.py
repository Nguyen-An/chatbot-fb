from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import ChatbotData
from datetime import datetime
from sqlalchemy import or_

def create_file_db(db: Session, file_info: ChatbotData):
    db.add(file_info)
    db.commit()
    db.refresh(file_info)
    return file_info

def get_files_db(db: Session, page: int, page_size: int, key_word: str = None):
    # Kiểm tra và xử lý page_size không hợp lệ
    if page_size <= 0:
        raise ValueError("Page size must be greater than 0.")
    
    # Tính toán offset và limit
    offset = (page - 1) * page_size
    limit = page_size

    # Nếu page == -1, lấy toàn bộ dữ liệu
    if page == -1:
        offset = 0
        limit = None  # None để không giới hạn số lượng

    # Query cơ bản
    query = db.query(ChatbotData)

    # Thêm điều kiện tìm kiếm nếu có từ khóa
    if key_word:
        query = query.filter(
            or_(
                ChatbotData.file_name.ilike(f"%{key_word}%"),  # Tìm kiếm theo tên file
                ChatbotData.describe.ilike(f"%{key_word}%")  # Tìm kiếm theo mô tả file (nếu có cột này)
            )
        )

    # Tổng số bản ghi (áp dụng cả tìm kiếm nếu có)
    total = query.count()

    # Lấy dữ liệu với phân trang
    items = query.offset(offset).limit(limit).all() if limit else query.all()

    # Tính tổng số trang
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "data": items,
    }

def delete_file(db: Session, key: str):
    file_to_delete = db.query(ChatbotData).filter(ChatbotData.key == key).one()
    db.delete(file_to_delete)
    db.commit()
    return file_to_delete