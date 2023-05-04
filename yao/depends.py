import json
import asyncio
from datetime import datetime
from functools import wraps
from typing import Optional, List, Union

from fastapi import Depends, Security, APIRouter, Query, Request, HTTPException, status
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

from config import OAUTH_TOKEN_URL, OAUTH_TOKEN_SCOPES, OAUTH_SECRET_KEY, OAUTH_ALGORITHM, OAUTH_LOGIN_SCOPES
from yao.db import session
from yao.helpers import token_payload
from yao.schema import ModelScreenParams
from yao.function.user.crud import CrudFunctionUser
from yao.function.user.schema import SchemasFunctionUser, SchemasFunctionScopes
from yao.function.log.crud import CrudFunctionLog
from yao.function.log.schema import SchemasFunctionStoreUpdate as SchemasStoreUpdateLog


# def model_screen_params(page: Optional[int] = 1, limit: Optional[int] = 25, quest_data: Optional[str] = None):
#     """列表筛选参数"""
#     order, where = [], []
#     if bool(quest_data):
#         quest_data = json.loads(quest_data) if quest_data else None
#         [order.extend(list(s.items())) for s in quest_data['sort']] if 'sort' in quest_data else None
#         where = [(w['key'], w['condition'], w['value']) for w in quest_data['where']] if 'where' in quest_data else None
#     return ModelScreenParams(page=page, limit=limit, order=order, where=where)


def model_post_screen_params(data: ModelScreenParams = None):
    """列表筛选参数"""
    order = []
    [order.extend(list(s.items())) for s in data.order]
    data.order = order
    where = [(w['key'], w['condition'], w['value']) for w in data.where if
             ('value' in w and (w['value'] or w['value'] is False or w['value'] == 0)) and (not "join" in w or "join" in w and not w['join'])]
    join = [(w['join'], [(w['key'], w['condition'], w['value'])], 'join') for w in data.where if
            ('value' in w and (w['value'] or w['value'] is False or w['value'] == 0)) and ("join" in w and w['join'])]
    data.where = where
    data.join = join
    return data


def model_screen_params(page: Optional[str] = None, limit: Optional[str] = None, where: Optional[str] = None, join: Optional[str] = None,
                        order: Optional[str] = None):
    """列表筛选参数"""
    data = ModelScreenParams(page=json.loads(page).get('value') if page else 1, limit=json.loads(limit).get('value') if limit else 25,
                             where=json.loads(where).get('value') if where else [], join=json.loads(join).get('value') if join else [],
                             order=json.loads(order).get('value') if order else [])

    return model_post_screen_params(data)


class OAuth2PasswordBearerOrForm(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization") or (await request.form()).get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerOrForm(tokenUrl=OAUTH_TOKEN_URL, scopes=OAUTH_TOKEN_SCOPES)


async def current_user_security(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    """
    解析加密字段
    :param security_scopes:
    :param token:
    :return:
    """
    payload = token_payload(security_scopes, token, OAUTH_SECRET_KEY, OAUTH_ALGORITHM)
    """处理授权用户实时情况"""
    # Todo
    """处理授权用户实时情况"""
    return SchemasFunctionUser(**payload)


async def auth_user(auth: SchemasFunctionUser = Security(current_user_security, scopes=[OAUTH_LOGIN_SCOPES]),
                    session: Session = Depends(session)):
    """
    demo
    :param auth:
    :param session:
    :return:
    """
    user = CrudFunctionUser.init().first(session=session, pk=auth.user_id)
    return SchemasFunctionScopes(user=user, prefix=auth.prefix, scopes=auth.scopes)


def item_prefix(callback):
    """
    处理 item prefix
    :param callback:
    :return:
    """

    @wraps(callback)
    async def wrapper(*args, **kwargs):
        if "item" in kwargs and "auth" in kwargs:
            item = kwargs.get("item")
            auth = kwargs.get("auth")
            item.prefix = item.prefix or auth.prefix
            kwargs.update({
                "item": item
            })
        response = await callback(*args, **kwargs) if asyncio.iscoroutinefunction(callback) else callback(*args, **kwargs)
        return response

    return wrapper


def item_name_prefix(callback):
    """
    处理 item 里name字段的前缀 prefix
    :param callback:
    :return:
    """

    @wraps(callback)
    async def wrapper(*args, **kwargs):
        if "item" in kwargs and "auth" in kwargs:
            item = kwargs.get("item")
            auth = kwargs.get("auth")
            if hasattr(item, "prefix"):
                item.prefix = item.prefix or auth.prefix
                if hasattr(item, 'name') and item.name:
                    item.name = "%s@%s" % (item.prefix, item.name.replace("%s@" % item.prefix, ""))
                kwargs.update({
                    "item": item
                })
        response = await callback(*args, **kwargs) if asyncio.iscoroutinefunction(callback) else callback(*args, **kwargs)
        return response

    return wrapper


def item_owns(callback):
    """
    处理 item 里owns字段
    :param callback:
    :return:
    """

    @wraps(callback)
    async def wrapper(*args, **kwargs):
        if "item" in kwargs and "auth" in kwargs:
            item = kwargs.get("item")
            auth = kwargs.get("auth")
            item.owns = auth.user.username
            kwargs.update({
                "item": item
            })
        response = await callback(*args, **kwargs) if asyncio.iscoroutinefunction(callback) else callback(*args, **kwargs)
        return response

    return wrapper


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def log_to_database(session=None, scope=None, methods=None, item=None, auth=None, **kwargs):
    prefix = item.prefix if item and hasattr(item, "prefix") and item.prefix else auth.prefix if auth else None
    if ('post' in methods and scope[:5] == ".post") or 'patch' in methods:
        CrudFunctionLog.init().store(
            session=session,
            item=SchemasStoreUpdateLog(prefix=prefix, scope=scope, methods=",".join(methods), data=json.loads(json.dumps(item.dict(exclude_unset=True), cls=DateEncoder)),
                                       username=auth.user.username),
            close=False)

    if 'delete' in methods:
        CrudFunctionLog.init().store(
            session=session,
            item=SchemasStoreUpdateLog(prefix=prefix, scope=scope, methods=",".join(methods), data=kwargs.get('uuids'), username=auth.user.username),
            close=False)


def route(path: str, module: str, router: APIRouter, methods: Optional[List[str]] = None, **kwargs):
    """
    重写路由修饰器
    :param path:
    :param module:
    :param router:
    :param methods:
    :param kwargs:
    :return:
    """

    if module:
        kwargs.update({"name": "{} {}".format(" ".join(methods), module)})

    def wrap(callback):
        @wraps(callback)
        @router.api_route(path=path.replace("_M_", module), methods=[method.upper() for method in methods], **kwargs)
        async def wrapper(*_args, **_kwargs):
            log_to_database(scope=path.replace("_M_", module), methods=methods, **_kwargs) or None
            return await callback(*_args, **_kwargs) if asyncio.iscoroutinefunction(callback) else callback(*_args, **_kwargs)

        return wrapper

    return wrap
