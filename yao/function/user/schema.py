from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator

from yao.schema import Schemas, SchemasPaginate
from yao.function.permission.schema import SchemasFunctionResponse, SchemasFunctionMenuMiniResponse
from yao.function.appointment.schema import SchemasFunctionAppointmentResponse
from yao.function.company.schema import SchemasFunctionResponse as companySchemasFunctionResponse


class SchemasFunctionUserResponse(BaseModel):
    """授权用户 返回"""
    uuid: Optional[str] = None
    prefix: Optional[str] = None
    username: Optional[str] = None
    user_phone: Optional[str] = None
    permissions: Optional[List[SchemasFunctionResponse]] = None
    appointments: Optional[List[SchemasFunctionAppointmentResponse]] = None
    available: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasPaginateItem(SchemasPaginate):
    items: List[SchemasFunctionUserResponse]


class SchemasFunctionUserStoreUpdate(BaseModel):
    """创建或者更新后台账户信息"""
    prefix: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    user_phone: Optional[str] = None
    available: Optional[bool] = True
    permissions: Optional[List[str]] = None
    appointments: Optional[List[str]] = None


class SchemasFunctionUserSafeUpdate(BaseModel):
    """创建或者更新后台账户信息"""
    password: Optional[str] = None
    user_phone: Optional[str] = None


class SchemasFunctionUser(BaseModel):
    """解析加密字段"""
    prefix: Optional[str] = None
    sub: Optional[str] = None
    user_id: Optional[int] = 0
    exp: Optional[int] = 0
    scopes: List[str] = []


class SchemasFunctionScopes(BaseModel):
    """验证授权后"""
    prefix: Optional[str] = None
    user: Optional[SchemasFunctionUserResponse] = None
    scopes: Optional[List[str]] = []


class SchemasLogin(BaseModel):
    """登录返回 token 兼容api"""
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class SchemasLoginResponse(SchemasLogin):
    """登录返回 token"""
    data: Optional[SchemasLogin] = None


class SchemasFunctionUserBriefly(BaseModel):
    """授权用户简要 返回"""
    username: Optional[str] = None
    user_phone: Optional[str] = None
    available: Optional[bool] = True

    class Config:
        orm_mode = True


class SchemasFunctionUserAndScopes(BaseModel):
    """获取授权返回"""
    prefix: Optional[str] = None
    user: Optional[SchemasFunctionUserBriefly] = None
    scopes: Optional[list] = None


class SchemasFunctionUserMeStatusResponse(Schemas):
    """登录授权用户 状态返回"""
    data: SchemasFunctionUserAndScopes


class SchemasParams(BaseModel):
    """参数"""
    appointments: Optional[List[SchemasFunctionAppointmentResponse]] = None
    permissions: Optional[List[SchemasFunctionMenuMiniResponse]] = None
    companies: Optional[List[companySchemasFunctionResponse]] = None
