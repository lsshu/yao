from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from yao.schema import SchemasPaginate


class SchemasFunctionResponse(BaseModel):
    """模型 返回"""
    uuid: Optional[str] = None
    name: Optional[str] = None  # 公司名称
    prefix_name: Optional[str] = None  # 公司前缀
    contact_name: Optional[str] = None  # 联系人
    contact_phone: Optional[str] = None  # 联系电话

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasFunctionStoreUpdate(BaseModel):
    """模型 提交"""
    name: Optional[str] = None  # 公司名称
    prefix_name: Optional[str] = None  # 公司前缀
    contact_name: Optional[str] = None  # 联系人
    contact_phone: Optional[str] = None  # 联系电话

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态


class SchemasFunctionPaginateItem(SchemasPaginate):
    items: List[SchemasFunctionResponse]


class SchemasParams(BaseModel):
    pass
