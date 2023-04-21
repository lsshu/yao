from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator

from yao.schema import SchemaPrefixNames, SchemasPaginate


class SchemasFunctionResponse(SchemaPrefixNames):
    """角色 返回"""
    uuid: Optional[str] = None
    parent_uuid: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasFunctionTreeResponse(SchemasFunctionResponse):
    children: Optional[List['SchemasFunctionTreeResponse']] = None


class SchemasFunctionPaginateItem(SchemasPaginate):
    items: Optional[List[SchemasFunctionTreeResponse]] = None


class SchemasFunctionStoreUpdate(BaseModel):
    """授权角色 提交"""
    prefix: Optional[str] = None
    parent_id: Optional[str] = None
    name: Optional[str] = None


class SchemasParams(BaseModel):
    departments: Optional[List[SchemasFunctionTreeResponse]] = None
