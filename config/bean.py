# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC
@File        ：bean.py
@IDE         ：PyCharm
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-17 20:46
-------------------------------------
'''
from typing import Any
from .response_status import SUCCESS, ERROR, UNAUTHORIZED
from sanic_ext.extensions.openapi.definitions import Response


class BaseResponseObj(object):
    def to_json(self):
        return self.__dict__


class BaseResponse:
    code: int
    message: str
    data: Any


Success = Response(content={"application/json": BaseResponse}, status=SUCCESS, description="请求成功")
Failure = Response(content={"application/json": BaseResponse}, status=ERROR, description="请求失败")


class BaseResponse(BaseResponseObj):
    def __init__(self, code: int, message: str | None, data: Any = None):
        self.code: int = code
        self.message: str | None = message
        self.data: Any = data

    def to_response(self):
        return {"body": self.to_json(), "status": self.code}


class SuccessResponse(BaseResponse):
    def __init__(self, message: str | None, data: Any = None):
        super().__init__(SUCCESS, message, data)


class FailureResponse(BaseResponse):
    def __init__(self, message: str | None, data: Any = None):
        super().__init__(ERROR, message, data)


class UnauthorizedResponse(BaseResponse):
    def __init__(self, message: str | None, data: Any = None):
        super().__init__(UNAUTHORIZED, message, data)
