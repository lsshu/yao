from typing import List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from yao.db import session as _session
from yao.depends import model_screen_params, model_post_screen_params, auth_user
from yao.schema import ModelScreenParams, Schemas, SchemasError
from yao.function.model import function_permission_name as name
from yao.function.permission.crud import CrudFunctionPermission
from yao.function.permission.schema import SchemasFunctionPaginateItem, SchemasFunctionResponse, SchemasFunctionStoreUpdate, \
    SchemasFunctionMenuStatusResponse
from yao.function.user.schema import SchemasFunctionScopes

router = APIRouter(tags=[name.replace('.', ' ').title()])

permission_scopes = [name, ]


@router.get('/{}'.format(name), name="get {}".format(name))
async def get_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CrudFunctionPermission.init().paginate(session=session, tree=True)
    return Schemas(data=SchemasFunctionPaginateItem(**db_model_list))


@router.post('/{}.post'.format(name), name="post {}".format(name))
async def post_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % name])):
    """
    :param session:
    :param params:
    :param auth:
    :return:
    """
    db_model_list = CrudFunctionPermission.init().paginate(session=session, tree=True)
    return Schemas(data=SchemasFunctionPaginateItem(**db_model_list))


@router.get('/{}.params'.format(name), name="get {}".format(name))
async def params_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.list" % name])):
    """
    :param session:
    :param auth:
    :return:
    """
    return Schemas(data={})


@router.get('/{}.menus'.format(name), name="get {}".format(name))
async def menus_permission_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user)):
    """
    :param session:
    :param auth:
    :return:
    """

    def query_fun(nodes):
        permissionClass = CrudFunctionPermission.model_class
        return nodes.filter(getattr(permissionClass, 'is_menu').is_(True)).filter(getattr(permissionClass, 'scope').in_(auth.scopes))

    db_model_list = CrudFunctionPermission.init().get_tree(session=session, query_function=query_fun)
    return SchemasFunctionMenuStatusResponse(data=db_model_list)


@router.post('/{}.menus.post'.format(name), name="post {}".format(name))
async def menus_permission_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user)):
    """
    :param session:
    :param auth:
    :return:
    """

    def query_fun(nodes):
        return nodes.filter(getattr(CrudFunctionPermission.init().model_class, 'is_menu').is_(True)).filter(
            getattr(CrudFunctionPermission.init().model_class, 'scope').in_(auth.scopes))

    db_model_list = CrudFunctionPermission.init().get_tree(session=session, query_function=query_fun)
    return SchemasFunctionMenuStatusResponse(data=db_model_list)


@router.get('/{}/{{pk}}'.format(name), name="get {}".format(name))
async def get_model(pk: int, session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.get" % name])):
    """
    :param pk:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionPermission.init(session=session).first(pk=pk)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    return Schemas(data=SchemasFunctionResponse(**db_model.to_dict()))


@router.post('/{}'.format(name), name="get {}".format(name))
async def store_model(item: SchemasFunctionStoreUpdate, session: Session = Depends(_session),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.store" % name])):
    """
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionPermission.init(session=session).first(where=("name", item.name))
    if db_model is not None:
        return SchemasError(message="数据已经存在！")
    bool_model = CrudFunctionPermission.init(session=session).store(item=item)
    return Schemas(data=SchemasFunctionResponse(**bool_model.to_dict()))


@router.put("/{}/{{pk}}".format(name), name="update {}".format(name))
async def update_put_model(pk: int, item: SchemasFunctionStoreUpdate, session: Session = Depends(_session),
                           auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % name])):
    """
    :param pk:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionPermission.init(session=session).first(pk=pk)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    bool_model = CrudFunctionPermission.init(session=session).update(pk=pk, item=item)
    return Schemas(data=SchemasFunctionResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}".format(name), name="update {}".format(name))
async def update_patch_model(pk: int, item: SchemasFunctionStoreUpdate, session: Session = Depends(_session),
                             auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % name])):
    """
    :param pk:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionPermission.init(session=session).first(pk=pk)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    bool_model = CrudFunctionPermission.init(session=session).update(pk=pk, item=item, exclude_unset=True)
    return Schemas(data=SchemasFunctionResponse(**bool_model.to_dict()))


@router.patch("/{}/{{pk}}/move_inside".format(name), name="update {}".format(name))
async def move_inside_permission_model(pk: int, inside_id: int, session: Session = Depends(_session),
                                       auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % name])):
    """
    移动到 inside_id 下
    :param pk:
    :param inside_id:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionPermission.init(session=session).move_inside(inside_id=inside_id, pk=pk)
    return Schemas(data=bool_model)


@router.patch("/{}/{{pk}}/move_after".format(name), name="update {}".format(name))
async def move_after_permission_model(pk: int, after_id: int, session: Session = Depends(_session),
                                      auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.update" % name])):
    """
    移动到 after_id 后
    :param pk:
    :param after_id:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionPermission.init(session=session).move_after(after_id=after_id, pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}/{{pk}}".format(name), name="delete {}".format(name))
async def delete_model(pk: int, session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.delete" % name])):
    """
    :param pk:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionPermission.init(session=session).delete(pk=pk)
    return Schemas(data=bool_model)


@router.delete("/{}".format(name), name="deletes {}".format(name))
async def delete_models(pks: List[int], session: Session = Depends(_session),
                        auth: SchemasFunctionScopes = Security(auth_user, scopes=permission_scopes + ["%s.delete" % name])):
    """
    :param pks:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionPermission.init(session=session).delete(pks=pks)
    return Schemas(data=bool_model)
