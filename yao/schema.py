from datetime import datetime
from typing import Optional, Union, List

from pydantic import BaseModel, validator

from config import SCHEMAS_SUCCESS_CODE, SCHEMAS_SUCCESS_STATUS, SCHEMAS_SUCCESS_MESSAGE, SCHEMAS_ERROR_CODE, SCHEMAS_ERROR_STATUS, SCHEMAS_ERROR_MESSAGE


class Schemas(BaseModel):
    """状态返回"""
    code: Optional[int] = SCHEMAS_SUCCESS_CODE
    status: Optional[str] = SCHEMAS_SUCCESS_STATUS
    message: Optional[str] = SCHEMAS_SUCCESS_MESSAGE
    data: Optional[Union[BaseModel, dict, list, str, bool, None]] = None


class SchemasError(BaseModel):
    """状态返回"""
    code: Optional[int] = SCHEMAS_ERROR_CODE
    status: Optional[str] = SCHEMAS_ERROR_STATUS
    message: Optional[str] = SCHEMAS_ERROR_MESSAGE
    data: Optional[Union[BaseModel, dict, list, str, bool, None]] = None


class SchemasPaginate(BaseModel):
    """分页"""
    items: Optional[list] = None  # 当前页的数据列表
    page: Optional[int] = None  # 当前页数
    pages: Optional[int] = None  # 总页数
    total: Optional[int] = None  # 总条数
    limit: Optional[int] = None  # 页条数


class ModelScreenParams(BaseModel):
    """获取列表默认参数"""
    page: Optional[int] = 1
    limit: Optional[int] = 25
    where: Optional[Union[dict, list]] = []
    join: Optional[Union[dict, list]] = []
    order: Optional[list] = []


class ModelScreenParamsForAll(BaseModel):
    """获取列表默认参数 不带分页"""
    where: Optional[Union[dict, list]] = []
    join: Optional[Union[dict, list]] = []
    order: Optional[list] = []


class SchemaPrefix(BaseModel):
    owns: Optional[str] = None

    @validator('owns')
    def p_owns(cls, name: str):
        return name.split("@", 1)[1] if name and len(name.split("@", 1)) == 2 else name


class SchemaPrefixNames(SchemaPrefix):
    name: Optional[str] = None

    @validator('name')
    def p_name(cls, name: str):
        return name.split("@", 1)[1] if name and len(name.split("@", 1)) == 2 else name


class SchemaParamsApi(SchemaPrefixNames):
    uuid: Optional[str] = None

    class Config:
        orm_mode = True


class ModelUUIDS(BaseModel):
    uuids: List[str] = None


class SchemasPrefixOwns(BaseModel):
    prefix: Optional[str] = None  # 公司前缀
    owns: Optional[str] = None  # 拥有


class SchemasAt(BaseModel):
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间
    deleted_at: Optional[datetime] = None  # 删除时间
