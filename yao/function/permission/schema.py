from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from yao.schema import SchemasPaginate, Schemas


class SchemasFunctionResponse(BaseModel):
    """权限 返回"""
    uuid: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[str] = None
    is_menu: Optional[bool] = True
    is_action: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    children: Optional[List['SchemasFunctionResponse']] = None

    class Config:
        orm_mode = True


class SchemasFunctionPaginateItem(SchemasPaginate):
    items: List[SchemasFunctionResponse]


class SchemasFunctionStoreUpdate(BaseModel):
    """授权角色 提交"""
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[str] = None
    is_menu: Optional[bool] = True
    is_action: Optional[bool] = True


class SchemasFunctionMiniResponse(BaseModel):
    """权限 返回"""
    uuid: Optional[str] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class SchemasFunctionMenuMiniResponse(SchemasFunctionMiniResponse):
    """权限 返回"""
    children: Optional[List['SchemasFunctionMenuMiniResponse']] = None

    class Config:
        orm_mode = True


class SchemasFunctionMenuMiniItemResponse(Schemas):
    """菜单树返回"""
    data: List[SchemasFunctionMenuMiniResponse]


class SchemasFunctionMenuResponse(BaseModel):
    """权限 返回"""
    uuid: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    scope: Optional[str] = None
    path: Optional[str] = None
    children: Optional[List['SchemasFunctionMenuResponse']] = None

    class Config:
        orm_mode = True


class SchemasFunctionMenuStatusResponse(Schemas):
    """菜单树返回"""
    data: List[SchemasFunctionMenuResponse]
