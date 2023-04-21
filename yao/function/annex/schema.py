from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from yao.schema import SchemaPrefixNames, SchemasPaginate


class SchemasFunctionAnnexeResponse(SchemaPrefixNames):
    """角色 返回"""
    md5: Optional[str] = None
    path: Optional[str] = None
    preview_path: Optional[str] = None
    size: Optional[int] = None

    class Config:
        orm_mode = True


class SchemasFunctionAnnexePaginateItem(SchemasPaginate):
    items: List[SchemasFunctionAnnexeResponse]


class SchemasFunctionAnnexeStoreUpdate(BaseModel):
    """提交"""
    prefix: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    md5: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class SchemasParams(BaseModel):
    pass


class SchemasUpLoadFileResponse(BaseModel):
    state: Optional[str] = "SUCCESS"  # 上传状态，上传成功时必须返回"SUCCESS"
    url: Optional[str] = None  # 返回的地址
    title: Optional[str] = None  # 新文件名
    original: Optional[str] = None  # 原始文件名
    type: Optional[str] = None  # 文件类型
    size: Optional[str] = None  # 文件大小
    list: Optional[List[dict]] = None


class SchemasUpLoadContentFile(BaseModel):
    path: str  # 目录
    content: str  # 内容
