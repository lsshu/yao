from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from yao.db import session as _session
from yao.depends import model_screen_params, model_post_screen_params, auth_user, route, item_name_prefix
from yao.schema import ModelScreenParams, Schemas, SchemasError
from yao.function.model import function_department_name as name
from yao.function.department.crud import CrudFunctionDepartment
from yao.function.department.schema import SchemasFunctionPaginateItem, SchemasParams, SchemasFunctionResponse, SchemasFunctionStoreUpdate
from yao.function.user.schema import SchemasFunctionScopes

router = APIRouter(tags=[name.replace('.', ' ').title()])

role_scopes = [name, ]


@route('/_M_', module=name, router=router, methods=['get'])
@item_name_prefix
async def get_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CrudFunctionDepartment.init().paginate(session=session, where=[('prefix', auth.prefix)], screen_params=params)
    return Schemas(data=SchemasFunctionPaginateItem(**db_model_list))


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
    db_model_list = CrudFunctionDepartment.init().paginate(session=session, screen_params=params, tree=True)
    return Schemas(data=SchemasFunctionPaginateItem(**db_model_list))


@route('/_M_.params', module=name, router=router, methods=['get'])
async def params_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param auth:
    :return:
    """
    data = {
        "departments": CrudFunctionDepartment.init().get_tree(session=session, where=[('prefix', auth.prefix)])
    }
    return Schemas(data=SchemasParams(**data))


@route('/_M_', module=name, router=router, methods=['post'])
@item_name_prefix
async def store_model(item: SchemasFunctionStoreUpdate, session: Session = Depends(_session),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % name])):
    """
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionDepartment.init().first(session=session, where=("name", item.name))
    if db_model is not None:
        return SchemasError(message="数据已经存在！")
    if item.parent_id:
        parent_model = CrudFunctionDepartment.init().first(session=session, uuid=item.parent_id)
        if parent_model:
            item.parent_id = parent_model.id
    bool_model = CrudFunctionDepartment.init().store(session=session, item=item)
    return Schemas(data=SchemasFunctionResponse(**bool_model.to_dict()))


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
    db_model = CrudFunctionDepartment.init().first(session=session, uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    CrudFunctionDepartment.init().update(session=session, uuid=uuid, item=item, exclude_unset=True)
    return Schemas()


@route("/_M_", module=name, router=router, methods=['delete'])
async def delete_models(uuids: List[str], session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.delete" % name])):
    """
    :param uuids:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionDepartment.init().delete(session=session, uuids=uuids, event=True)
    return Schemas(data=bool_model)
