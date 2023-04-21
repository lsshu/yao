from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from yao.db import session as _session
from yao.depends import model_screen_params, model_post_screen_params, auth_user, route, item_name_prefix
from yao.schema import ModelScreenParams, Schemas, SchemasError
from yao.function.model import function_log_name as name
from yao.function.log.crud import CrudFunctionLog
from yao.function.log.schema import SchemasFunctionPaginateItem, SchemasFunctionParams, SchemasFunctionStoreUpdate
from yao.function.user.schema import SchemasFunctionScopes

router = APIRouter(tags=[name.replace('.', ' ').title()])

role_scopes = [name, ]


@route('/_M_', module=name, router=router, methods=['get'])
async def post_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_screen_params),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CrudFunctionLog.init().paginate(session=session, where=[('prefix', auth.prefix)], screen_params=params)
    return Schemas(data=SchemasFunctionPaginateItem(**db_model_list))


@route('/_M_.post', module=name, router=router, methods=['post'])
async def post_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CrudFunctionLog.init().paginate(session=session, screen_params=params)
    return Schemas(data=SchemasFunctionPaginateItem(**db_model_list))


@route('/_M_.params', module=name, router=router, methods=['get'])
async def params_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param auth:
    :return:
    """
    data = {}
    return Schemas(data=SchemasFunctionParams(**data))


@route("/_M_/{uuid}", module=name, router=router, methods=['patch'])
@item_name_prefix
async def update_patch_model(uuid: str, item: SchemasFunctionStoreUpdate, session: Session = Depends(_session),
                             auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.update" % name])):
    """
    :param uuid:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionLog.init().first(session=session, uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    CrudFunctionLog.init().update(session=session, uuid=uuid, item=item, exclude_unset=True)
    return Schemas()


@route("/_M_", module=name, router=router, methods=['delete'])
async def delete_models(uuids: List[str], session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.delete" % name])):
    """
    :param uuids:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionLog.init().delete(session=session, uuids=uuids, event=True)
    return Schemas(data=bool_model)
