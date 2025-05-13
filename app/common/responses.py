from fastapi import HTTPException, status
from .responses_msg import *
from fastapi.responses import JSONResponse

# Phản hồi cho 200 OK
ok_response = {
    "description": "Request was successful",
    "content": {
        "application/json": {
            "example": {
                "message": "Success",
                "data": {}
            }
        }
    }
}

# Phản hồi cho 400 Bad Request
bad_request_response = {
    "description": "Invalid request parameters",
    "content": {
        "application/json": {
            "example": {
                "detail": "Bad Request"
            }
        }
    }
}

# Phản hồi cho 404 Not Found
not_found_response = {
    "description": "Item not found",
    "content": {
        "application/json": {
            "example": {
                "detail": "Not Found"
            }
        }
    }
}

# Phản hồi cho 500 Internal Server Error
internal_server_error_response = {
    "description": "Internal server error",
    "content": {
        "application/json": {
            "example": {
                "detail": "Internal Server Error"
            }
        }
    }
}

common_responses = {
    status.HTTP_200_OK: ok_response,
    status.HTTP_400_BAD_REQUEST: bad_request_response,
    status.HTTP_404_NOT_FOUND: not_found_response,
    status.HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_response
}

def OK(data: any = None):
    if data is None:
        return {
            "message": STT_CODE.get("SUCCESS", "")
        }
    else:
        return {
            "message": STT_CODE.get("SUCCESS", ""),
            "data": data
        }
    
def return_exception(e):
    e.status_code = getattr(e, 'status_code', 500)
    if e.status_code == 400:
        return JSONResponse(status_code=400, content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code")))
    if e.status_code == 404:
        return JSONResponse(status_code=404, content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code")))
    if e.status_code == 401:
        return JSONResponse(status_code=401, content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code")))
    if e.status_code == 403:
        return JSONResponse(status_code=403, content=create_error_response(e.detail, STT_CODE.get(e.detail, "Unknown error code")))
    
    return JSONResponse(status_code=500, content=create_error_response("INTERNAL_SERVER_ERROR", STT_CODE.get("INTERNAL_SERVER_ERROR", "Unknown error code")))
