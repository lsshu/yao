from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from yao.db import session as _session
from yao.depends import model_screen_params, model_post_screen_params, auth_user, route, item_name_prefix
from yao.schema import ModelScreenParams, Schemas, SchemasError
from yao.function.model import function_appointment_name as name
from yao.function.permission.crud import CrudFunctionPermission
from yao.function.appointment.crud import CrudFunctionAppointment
from yao.function.appointment.schema import SchemasFunctionAppointmentPaginateItem, SchemasFunctionAppointmentResponse, SchemasFunctionAppointmentStoreUpdate, SchemasParams
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
    db_model_list = CrudFunctionAppointment.init().paginate(session=session, where=[('prefix', auth.prefix)], screen_params=params)
    return Schemas(data=SchemasFunctionAppointmentPaginateItem(**db_model_list))


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
    db_model_list = CrudFunctionAppointment.init().paginate(session=session, screen_params=params)
    return Schemas(data=SchemasFunctionAppointmentPaginateItem(**db_model_list))


@route('/_M_.params', module=name, router=router, methods=['get'])
async def params_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.list" % name])):
    """
    :param session:
    :param auth:
    :return:
    """

    data = {
        "permissions": CrudFunctionPermission.init().get_tree(session=session, where=[('scope', "in", auth.scopes)])
    }
    return Schemas(data=SchemasParams(**data))


@route('/_M_', module=name, router=router, methods=['post'])
@item_name_prefix
async def store_model(item: SchemasFunctionAppointmentStoreUpdate, session: Session = Depends(_session),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % name])):
    """
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionAppointment.init().first(session=session, where=("name", item.name))
    if db_model is not None:
        return SchemasError(message="数据已经存在！")
    bool_model = CrudFunctionAppointment.init().store(session=session, item=item)
    return Schemas(data=SchemasFunctionAppointmentResponse(**bool_model.to_dict()))


@route("/_M_/{uuid}", module=name, router=router, methods=['patch'])
@item_name_prefix
async def update_patch_model(uuid: str, item: SchemasFunctionAppointmentStoreUpdate, session: Session = Depends(_session),
                             auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.update" % name])):
    """
    :param uuid:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionAppointment.init().first(session=session, uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    CrudFunctionAppointment.init().update(session=session, uuid=uuid, item=item, exclude_unset=True)
    return Schemas()


@route("/_M_", module=name, router=router, methods=['delete'])
async def delete_models(uuids: List[str], session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.delete" % name])):
    """
    :param uuids:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionAppointment.init().delete(session=session, uuids=uuids, event=True)
    return Schemas(data=bool_model)
