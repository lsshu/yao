from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from yao.schema import SchemaPrefixNames, SchemasPaginate
from yao.function.permission.schema import SchemasFunctionMiniResponse, SchemasFunctionMenuMiniResponse


class SchemasFunctionAppointmentResponse(SchemaPrefixNames):
    """角色 返回"""
    uuid: Optional[str] = None
    name: Optional[str] = None
    permissions: Optional[List[SchemasFunctionMiniResponse]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasFunctionAppointmentPaginateItem(SchemasPaginate):
    items: List[SchemasFunctionAppointmentResponse]


class SchemasFunctionAppointmentStoreUpdate(BaseModel):
    """授权角色 提交"""
    prefix: Optional[str] = None
    name: Optional[str] = None
    scopes: Optional[str] = None
    permissions: Optional[List[str]] = None


class SchemasParams(BaseModel):
    permissions: Optional[List[SchemasFunctionMenuMiniResponse]] = None
