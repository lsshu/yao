from typing import List, Optional

from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES, OAUTH_LOGIN_SCOPES, DEFAULT_FUNCTION_COMPANY, OAUTH_ADMIN_USERS, OAUTH_SECRET_KEY, OAUTH_ALGORITHM, \
    OAUTH_TOKEN_URI, OAUTH_SCOPES_URI, OAUTH_ME_URI
from yao.db import session as _session
from yao.depends import model_screen_params, model_post_screen_params, auth_user
from yao.helpers import token_access_token, token_verify_password
from yao.schema import Schemas, SchemasError, ModelScreenParams
from yao.function.model import function_user_name as name
from yao.function.user.crud import CrudFunctionUser
from yao.function.user.schema import SchemasFunctionScopes, SchemasLoginResponse, SchemasLogin, SchemasFunctionUserMeStatusResponse, SchemasPaginateItem, SchemasParams, \
    SchemasFunctionUserResponse, SchemasFunctionUserStoreUpdate, SchemasFunctionUserSafeUpdate, SchemasBindAuth

router = APIRouter(tags=[name.replace('.', ' ').title()])

user_scopes = [name, ]


def authenticate_user(session: Session, username: str, password: str):
    """
    验证用户信息
    :param session:
    :param username:
    :param password:
    :return:
    """
    user = CrudFunctionUser.init().first(session=session, where=[("username", username), ("available", True)])
    if not user or not token_verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号或者密码不正确！")
    return user


def token_authenticate_access_token(session, username: str, password: str, scopes: list) -> str:
    """
    认证用户且生成用户token
    :param session:
    :param username:
    :param password:
    :param scopes:
    :return:
    """
    from datetime import timedelta
    user = authenticate_user(session=session, username=username, password=password)
    access_token_expires = timedelta(minutes=int(OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES))
    scopes = scopes + [OAUTH_LOGIN_SCOPES]
    """处理用户拥有的权限"""
    # Todo user.roles user.permission
    if user.username and user.username.split("@")[0] == DEFAULT_FUNCTION_COMPANY.get("prefix_name") and user.username.split("@")[1] in OAUTH_ADMIN_USERS:
        from yao.function.permission.crud import CrudFunctionPermission
        permissions = CrudFunctionPermission.init().get(session=session)
        scopes = scopes + [permission.scope for permission in permissions]
    else:
        # 获取用户权限
        scopes = scopes + [permission.scope for permission in user.permissions]
        # 获取用户角色权限
        scopes = scopes + [scope for appointment in user.appointments for scope in (appointment.scopes.split(' '))]
    """处理用户拥有的权限"""
    return token_access_token(
        data={"sub": user.username, "user_id": user.id, "prefix": user.prefix, "scopes": list(set(scopes))},
        key=OAUTH_SECRET_KEY,
        algorithm=OAUTH_ALGORITHM,
        expires_delta=access_token_expires
    )


@router.post(OAUTH_TOKEN_URI)
async def login_for_access_token(session: Session = Depends(_session), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    获取登录授权:
    - **form_data**: 登录数据
    """
    access_token = token_authenticate_access_token(
        session=session,
        username=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes
    )
    return SchemasLoginResponse(data=SchemasLogin(access_token=access_token, token_type="bearer"), access_token=access_token, token_type="bearer")


@router.get(OAUTH_SCOPES_URI)
async def get_scopes(auth: SchemasFunctionScopes = Security(auth_user)):
    """
    获取登录授权:
    """
    return Schemas(data=auth)


@router.get(OAUTH_ME_URI)
async def get_me(auth: SchemasFunctionScopes = Security(auth_user)):
    """
    获取登录授权的用户信息:
    """
    return Schemas(data=auth.user)


@router.patch(OAUTH_ME_URI)
async def patch_me(item: SchemasFunctionUserSafeUpdate, session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user)):
    """
    更新登录授权用户的信息:
    """
    bool_model = CrudFunctionUser.init(session=session).update(uuid=auth.user.uuid, item=item)
    return Schemas(data=SchemasFunctionUserResponse(**bool_model.to_dict()))


@router.get('/{}'.format(name), name="get {}".format(name))
async def get_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_screen_params),
                     auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % name])):
    """
    获取授权用户列表
    - **:param session**:
    - **:param params**:
    - **:param auth**:
    - **:return**:
    """
    if auth.user.username and auth.user.username.split("@")[0] == DEFAULT_FUNCTION_COMPANY.get("prefix_name") and auth.user.username.split("@")[1] in OAUTH_ADMIN_USERS:
        db_model_list = CrudFunctionUser.init().paginate(session=session, where=[("parent_id", None) if len(params.where) == 0 else None], screen_params=params)
    else:
        db_model_list = CrudFunctionUser.init().paginate(session=session, where=[('prefix', auth.prefix), ("parent_id", None) if len(params.where) == 0 else None],
                                                         screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.post('/{}.post'.format(name), name="post {}".format(name))
async def post_models(session: Session = Depends(_session), params: ModelScreenParams = Depends(model_post_screen_params),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % name])):
    """
    获取授权用户列表
    - **:param session**:
    - **:param params**:
    - **:param auth**:
    - **:return**:
    """
    db_model_list = CrudFunctionUser.init().paginate(session=session, screen_params=params)
    return Schemas(data=SchemasPaginateItem(**db_model_list))


@router.get('/{}.params'.format(name), name="get {}".format(name))
async def params_models(session: Session = Depends(_session), auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.list" % name])):
    """
    :param session:
    :param auth:
    :return:
    """
    from yao.function.permission.crud import CrudFunctionPermission
    from yao.function.appointment.crud import CrudFunctionAppointment
    if auth.user.username and auth.user.username.split("@")[0] == DEFAULT_FUNCTION_COMPANY.get("prefix_name") and auth.user.username.split("@")[1] in OAUTH_ADMIN_USERS:
        from yao.function.company.crud import CrudFunctionCompany
        data = {
            "appointments": CrudFunctionAppointment.init().get(session=session),
            "permissions": CrudFunctionPermission.init().get_tree(session=session, json=True),
            "companies": CrudFunctionCompany.init().get(session=session)
        }
    else:
        has_appointment_uuids = [appointment.uuid for appointment in auth.user.appointments]
        data = {
            "appointments": CrudFunctionAppointment.init().get(session=session, where=[("__or", [("prefix", auth.prefix), ("uuid", "in", has_appointment_uuids)])]),
            "permissions": CrudFunctionPermission.init().get_tree(session=session, where=[("scope", "in", auth.scopes)], json=True)
        }
    return Schemas(data=SchemasParams(**data))


@router.get('/{}/{{uuid}}'.format(name), name="get {}".format(name))
async def get_model(uuid: str, session: Session = Depends(_session),
                    auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.get" % name])):
    """
    :param uuid:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionUser.init(session=session).first(uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    return Schemas(data=SchemasFunctionUserResponse(**db_model.to_dict()))


@router.post('/{}'.format(name), name="get {}".format(name))
async def store_model(item: SchemasFunctionUserStoreUpdate, session: Session = Depends(_session),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.store" % name])):
    """
    :param item:
    :param session
    :param auth:
    :return:
    """
    item.prefix = item.prefix or auth.prefix
    item.username = "%s@%s" % (item.prefix, item.username.replace("%s@" % item.prefix, ""))
    db_model = CrudFunctionUser.init().first(session=session, where=("username", item.username))
    if db_model is not None:
        return SchemasError(message="数据已经存在！")
    bool_model = CrudFunctionUser.init().store(session=session, item=item)
    return Schemas(data=SchemasFunctionUserResponse(**bool_model.to_dict()))


@router.put("/{}/{{uuid}}".format(name), name="update {}".format(name))
async def update_put_model(uuid: str, item: SchemasFunctionUserStoreUpdate, session: Session = Depends(_session),
                           auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.update" % name])):
    """
    :param uuid:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    db_model = CrudFunctionUser.init(session=session).first(uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    item.prefix = item.prefix or auth.prefix
    item.username = "%s@%s" % (auth.prefix, item.username)
    CrudFunctionUser.init(session=session).update(uuid=uuid, item=item, exclude_unset=False)
    return Schemas()


@router.patch("/{}/{{uuid}}".format(name), name="update {}".format(name))
async def update_patch_model(uuid: str, item: SchemasFunctionUserStoreUpdate, session: Session = Depends(_session),
                             auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.update" % name])):
    """
    :param uuid:
    :param item:
    :param session:
    :param auth:
    :return:
    """
    item.prefix = item.prefix or auth.prefix
    item.username = "%s@%s" % (item.prefix, item.username.replace("%s@" % item.prefix, ""))
    db_model = CrudFunctionUser.init().first(session=session, uuid=uuid)
    if db_model is None:
        return SchemasError(message="数据没有找到！")
    CrudFunctionUser.init().update(session=session, uuid=uuid, item=item, exclude_unset=True, event=True, close=True)
    return Schemas()


@router.delete("/{}/{{uuid}}".format(name), name="delete {}".format(name))
async def delete_model(uuid: str, session: Session = Depends(_session),
                       auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.delete" % name])):
    """
    :param uuid:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionUser.init(session=session).delete(session=session, uuid=uuid)
    return Schemas(data=bool_model)


@router.delete("/{}".format(name), name="deletes {}".format(name))
async def delete_models(pks: List[int], session: Session = Depends(_session),
                        auth: SchemasFunctionScopes = Security(auth_user, scopes=user_scopes + ["%s.delete" % name])):
    """
    :param pks:
    :param session:
    :param auth:
    :return:
    """
    bool_model = CrudFunctionUser.init(session=session).delete(pks=pks)
    return Schemas(data=bool_model)


@router.post('/{}.bind.auth'.format(name), name="post {}".format(name))
async def bind_auth(item: SchemasBindAuth, session: Session = Depends(_session)):
    """
    :param item:
    :param session
    :return:
    """
    try:
        from config import PROGRAMAPPID, PROGRAMAPPSECRET
    except:
        return SchemasError(data="配置出错！")
    from yao.wxamp.base import AMP
    try:
        amp = AMP(PROGRAMAPPID, PROGRAMAPPSECRET)
        res = amp.code2session(item.code)
        openid = res.get("openid", None)
        if item.scene and openid:
            db_model = CrudFunctionUser.init().first(session=session, uuid=item.scene)
            auth_data = db_model.auth_data if db_model and type(db_model.auth_data) is dict else {}
            auth_data.update({
                item.type: {"openid": openid}
            })
            _item = SchemasFunctionUserStoreUpdate(auth_data=auth_data)
            CrudFunctionUser.init().update(session=session, uuid=item.scene, item=_item, exclude_unset=True, event=True, close=True)
            return Schemas(data="已经成功获取到授权，可以关闭当前窗口！")
    except:
        return SchemasError(data="授权出错！")


@router.get('/auth/mp/{user_uuid}', name="get {}".format(name))
async def mp_auth(user_uuid: str, session: Session = Depends(_session)):
    """
    :param user_uuid
    :param session
    :return:
    """
    from config import HOME_URL
    try:
        from config import MPAPPID, MPAPPSECRET
    except:
        return SchemasError(data="配置出错！")
    from yao.wxmp.base import MP
    try:
        mp = MP(MPAPPID, MPAPPSECRET)
        redirect_url = "%sapi/auth/mp_callback" % HOME_URL
        return mp.get_or_to_auth_url(redirect_uri=redirect_url, state=user_uuid, fastapi_return=True)
    except:
        return SchemasError(data="授权出错！")


@router.get('/auth/mp_callback', name="get {}".format(name))
async def callback_auth(code, state: str, session: Session = Depends(_session)):
    """
    :param code
    :param state user_uuid
    :param session
    :return:
    """
    try:
        from config import MPAPPID, MPAPPSECRET
    except:
        return SchemasError(data="配置出错！")
    from yao.wxmp.base import MP
    try:
        mp = MP(MPAPPID, MPAPPSECRET)
        res = mp.code_to_openid(code=code)
        openid = res.get("openid", None)

        if state and openid:
            db_model = CrudFunctionUser.init().first(session=session, uuid=state)
            auth_data = db_model.auth_data if db_model and type(db_model.auth_data) is dict else {}
            auth_data.update({
                "mp": {"openid": openid}
            })
            _item = SchemasFunctionUserStoreUpdate(auth_data=auth_data)
            CrudFunctionUser.init().update(session=session, uuid=state, item=_item, exclude_unset=True, close=True)
            content = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
                        <meta http-equiv="X-UA-Compatible" content="ie=edge">
                        <title>授权成功!</title>
                    </head>
                    <body>
                    <h1 style="text-align: center;margin:100px auto;width:100%;color:green">已经成功获取到授权，可以关闭当前窗口！</h1>
                    </body>
                    </html>
                    """
            return HTMLResponse(content=content, status_code=200)
    except:
        pass
    content = """
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
                <title>授权出错!</title>
            </head>
            <body>
            <h1 style="text-align: center;margin:100px auto;width:100%;color:red">授权出错！</h1>
            </body>
            </html>
            """
    return HTMLResponse(content=content, status_code=200)
