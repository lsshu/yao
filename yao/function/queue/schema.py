from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from yao.schema import SchemasPaginate, SchemaPrefixNames
from app.stats.schema import SchemasPrefixOwns
from app.advertising.application.schema import SchemasResponse as SchemasApplicationResponse


class SchemasResponse(SchemaPrefixNames):
    """模型 返回"""
    uuid: Optional[str] = None
    username: Optional[str] = None  # 用户
    priority: Optional[int] = None  # 优先级
    scope: Optional[str] = None  # scope
    data: Optional[dict] = None  # Data
    key: Optional[str] = None  # 去重Key
    start_at: Optional[datetime] = None  # 开始时间
    stop_at: Optional[datetime] = None  # 结束时间
    progress: Optional[str] = None  # 进度条
    progress_text: Optional[str] = None  # 进度条
    retry: Optional[int] = None  # 重试次数
    queue_status: Optional[int] = None  # 状态

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchemasStoreUpdate(SchemasPrefixOwns):
    """模型 提交"""
    username: Optional[str] = None  # 用户
    priority: Optional[int] = None  # 优先级
    scope: Optional[str] = None  # scope
    data: Optional[dict] = None  # Data
    key: Optional[str] = None  # 去重Key
    start_at: Optional[datetime] = None  # 开始时间
    stop_at: Optional[datetime] = None  # 结束时间
    progress: Optional[str] = None  # 进度条
    progress_text: Optional[str] = None  # 进度条
    retry: Optional[int] = None  # 重试次数
    queue_status: Optional[int] = None  # 状态 0未运行 1成功 2失败

    remarks: Optional[str] = None  # 备注
    sort: Optional[int] = None  # 排序
    status: Optional[bool] = None  # 状态


class SchemasPaginateItem(SchemasPaginate):
    items: List[SchemasResponse]


class SchemasParams(BaseModel):
    applications: Optional[List[SchemasApplicationResponse]]


class SchemasQueueAuth(BaseModel):
    prefix: Optional[str] = None
    username: Optional[str] = None
