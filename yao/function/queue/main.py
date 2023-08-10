from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from yao.db import session as _session
from yao.depends import model_screen_params, model_post_screen_params, auth_user, route, item_owns, item_name_prefix
from yao.schema import ModelScreenParams, Schemas, SchemasError
from yao.function.model import function_queue_name as name
from yao.function.queue.crud import Crud
from yao.function.queue.schema import SchemasPaginateItem, SchemasParams, SchemasResponse, SchemasStoreUpdate
from yao.function.user.schema import SchemasFunctionScopes

from app.advertising.application.crud import Crud as APPLICATIONSCrud

router = APIRouter(tags=[name.replace('.', ' ').title()])

role_scopes = [name, ]


@route('/_M_', module=name, router=router, methods=['get'])
@item_name_prefix
async def post_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_screen_params),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = Crud.init().paginate(session=session, where=[('prefix', auth.prefix)], screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@route('/_M_.post', module=name, router=router, methods=['post'])
@item_name_prefix
async def post_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = Crud.init().paginate(session=session, where=[('prefix', auth.prefix)], screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@route('/_M_.params', module=name, router=router, methods=['get'])
async def params_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param auth:
    :return:
    """
    data = {
        "applications": APPLICATIONSCrud.init().get(session=session, where=[('prefix', auth.prefix)]),
    }
    return Schemas(data=SchemasParams(**data))


@route('/_M_', module=name, router=router, methods=['post'])
@item_name_prefix
@item_owns
async def store_model(item: SchemasStoreUpdate, session: Session = Depends(_session),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % name])):
    """
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = Crud.init().first(session=session, where=("userName", item.userName))
    if db_model is not None:
        return SchemasError(message="数据已经存在！")
    bool_model = Crud.init().store(session=session, item=item)
    return Schemas(data=SchemasResponse(**bool_model.to_dict()))


@route("/_M_/{uuid}", module=name, router=router, methods=['patch'])
@item_name_prefix
async def update_patch_model(uuid: str, item: SchemasStoreUpdate, session: Session = Depends(_session),
                             auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.update" % name])):
    """
    :param uuid:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = Crud.init().first(session=session, uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    if item.queue_status == 0:
        item.start_at = None
        item.stop_at = None
        item.progress = None
        item.progress_text = None
        item.retry = 0
    Crud.init().update(session=session, uuid=uuid, item=item, event=True, exclude_unset=True)
    return Schemas()


@route("/_M_", module=name, router=router, methods=['delete'])
async def delete_models(uuids: List[str], session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.delete" % name])):
    """
    :param uuids:
    :param session:
    :param auth:
    :return:
    """
    bool_model = Crud.init().delete(session=session, uuids=uuids, event=True)
    return Schemas(data=bool_model)
