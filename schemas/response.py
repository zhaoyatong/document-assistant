from pydantic import BaseModel
from typing import Optional, Generic, TypeVar


class ResponseCode:
    SUCCESS = 200
    BadRequest = 400  # 请求错误
    Unauthorized = 401  # 未授权
    Forbidden = 403  # 无权限
    NotFound = 404  # 未找到
    InternalServerError = 500  # 服务器内部错误

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: str =  ""
    status_code: int = ResponseCode.SUCCESS
    data: Optional[T] = None
