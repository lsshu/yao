from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, validator

from yao.schema import SchemasPaginate


class SchemasFunctionResponse(BaseModel):
    """模型 返回"""
    uuid: Optional[str] = None
    scope: Optional[str] = None  # scope
    methods: Optional[str] = None  # methods
    data: Optional[Union[dict, list]] = None  # Data
    username: Optional[str] = None  # 权限

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('username')
    def p_name(cls, username: str):
        return username.split("@", 1)[1]

    class Config:
        orm_mode = True


class SchemasFunctionStoreUpdate(BaseModel):
    """模型 提交"""
    prefix: Optional[str] = None
    uuid: Optional[str] = None
    scope: Optional[str] = None  # scope
    methods: Optional[str] = None  # methods
    data: Optional[Union[dict, list]] = None  # Data
    username: Optional[str] = None  # 权限

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态


class SchemasFunctionPaginateItem(SchemasPaginate):
    items: List[SchemasFunctionResponse]


class SchemasFunctionParams(BaseModel):
    pass
