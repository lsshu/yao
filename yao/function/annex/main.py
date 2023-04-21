import json
import os
import requests
import filetype

from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional

from yao.db import session as _session
from yao.depends import auth_user, route, item_prefix
from yao.schema import Schemas, SchemasError
from yao.function.model import function_annex_name as name
from yao.function.annex.crud import CrudFunctionAnnexe
from yao.function.annex.schema import SchemasFunctionAnnexeResponse, SchemasFunctionAnnexeStoreUpdate, SchemasUpLoadFileResponse, SchemasUpLoadContentFile
from yao.function.user.schema import SchemasFunctionScopes
from config import UPLOAD_DIR
from yao.method import md5_bytes, write_file

router = APIRouter(tags=[name.replace('.', ' ').title()])

role_scopes = [name, ]


@route('/_M_', module=name, router=router, methods=['post'])
async def store_model(file: UploadFile = File(...), session: Session = Depends(_session),
                      auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % name])):
    """
    :param file:
    :param session:
    :param auth:
    :return:
    """
    content = await file.read()
    md5 = md5_bytes(content)
    size = len(content)

    db_model = CrudFunctionAnnexe.init().first(session=session, where=[("md5", md5), ("prefix", auth.prefix)])
    if db_model is None:
        path = os.path.join(UPLOAD_DIR, auth.prefix, os.path.split(file.content_type)[0], "{}{}".format(md5, os.path.splitext(file.filename)[-1]))
        bool_res = write_file(path, content)
        if bool_res:
            try:
                from PIL import Image
                img = Image.open(path)
                width, height = img.size
            except:
                width, height = (0, 0)
            CrudFunctionAnnexe.init().store(session=session,
                                            item=SchemasFunctionAnnexeStoreUpdate(
                                                prefix=auth.prefix,
                                                filename=file.filename,
                                                content_type=file.content_type,
                                                md5=md5, path=path, size=size, width=width, height=height))
            db_model = CrudFunctionAnnexe.init().first(session=session, where=("md5", md5))
    return Schemas(data=SchemasFunctionAnnexeResponse(**db_model.to_dict()))


@route('/_M_.ueditor', module=name, router=router, methods=['get'])
@item_prefix
async def get_ueditor_models(action: str, session: Session = Depends(_session)):
    """
    :param action:
    :param session:
    :return:
    """
    # 前后端通信相关的配置,注释只允许使用多行方式 
    defaultConfig = {
        # 上传图片配置项 
        "imageActionName": "uploadimage",  # 执行上传图片的action名称 
        "imageFieldName": "file",  # 提交的图片表单名称
        "imageMaxSize": 2048000,  # 上传大小限制，单位B 
        "imageAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # 上传图片格式显示 
        "imageCompressEnable": True,  # 是否压缩图片,默认是True 
        "imageCompressBorder": 1600,  # 图片压缩最长边限制 
        "imageInsertAlign": "none",  # 插入的图片浮动方式 
        "imageUrlPrefix": "",  # 图片访问路径前缀

        # 涂鸦图片上传配置项 
        "scrawlActionName": "uploadscrawl",  # 执行上传涂鸦的action名称 
        "scrawlFieldName": "file",  # 提交的图片表单名称
        "scrawlPathFormat": "/ueditor/php/upload/image/{yyyy}{mm}{dd}/{time}{rand:6}",  # 上传保存路径,可以自定义保存路径和文件名格式 
        "scrawlMaxSize": 2048000,  # 上传大小限制，单位B 
        "scrawlUrlPrefix": "",  # 图片访问路径前缀 
        "scrawlInsertAlign": "none",

        # 截图工具上传 
        "snapscreenActionName": "uploadimage",  # 执行上传截图的action名称 
        "snapscreenPathFormat": "/ueditor/php/upload/image/{yyyy}{mm}{dd}/{time}{rand:6}",  # 上传保存路径,可以自定义保存路径和文件名格式 
        "snapscreenUrlPrefix": "",  # 图片访问路径前缀 
        "snapscreenInsertAlign": "none",  # 插入的图片浮动方式 

        # 抓取远程图片配置 
        "catcherLocalDomain": ["127.0.0.1", "localhost", "img.baidu.com"],
        "catcherActionName": "catchimage",  # 执行抓取远程图片的action名称 
        "catcherFieldName": "source",  # 提交的图片列表表单名称 
        "catcherPathFormat": "/ueditor/php/upload/image/{yyyy}{mm}{dd}/{time}{rand:6}",  # 上传保存路径,可以自定义保存路径和文件名格式 
        "catcherUrlPrefix": "",  # 图片访问路径前缀 
        "catcherMaxSize": 2048000,  # 上传大小限制，单位B 
        "catcherAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # 抓取图片格式显示 

        # 上传视频配置 
        "videoActionName": "uploadvideo",  # 执行上传视频的action名称 
        "videoFieldName": "file",  # 提交的视频表单名称
        "videoPathFormat": "/ueditor/php/upload/video/{yyyy}{mm}{dd}/{time}{rand:6}",  # 上传保存路径,可以自定义保存路径和文件名格式 
        "videoUrlPrefix": "",  # 视频访问路径前缀 
        "videoMaxSize": 102400000,  # 上传大小限制，单位B，默认100MB 
        "videoAllowFiles": [
            ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
            ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid"],  # 上传视频格式显示 

        # 上传文件配置 
        "fileActionName": "uploadfile",  # controller里,执行上传视频的action名称 
        "fileFieldName": "file",  # 提交的文件表单名称
        "filePathFormat": "/ueditor/php/upload/file/{yyyy}{mm}{dd}/{time}{rand:6}",  # 上传保存路径,可以自定义保存路径和文件名格式 
        "fileUrlPrefix": "",  # 文件访问路径前缀 
        "fileMaxSize": 51200000,  # 上传大小限制，单位B，默认50MB 
        "fileAllowFiles": [
            ".png", ".jpg", ".jpeg", ".gif", ".bmp",
            ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
            ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
            ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
            ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml"
        ],  # 上传文件格式显示 

        # 列出指定目录下的图片 
        "imageManagerActionName": "listimage",  # 执行图片管理的action名称 
        "imageManagerListPath": "/ueditor/php/upload/image/",  # 指定要列出图片的目录 
        "imageManagerListSize": 20,  # 每次列出文件数量 
        "imageManagerUrlPrefix": "",  # 图片访问路径前缀 
        "imageManagerInsertAlign": "none",  # 插入的图片浮动方式 
        "imageManagerAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # 列出的文件类型 

        # 列出指定目录下的文件 
        "fileManagerActionName": "listfile",  # 执行文件管理的action名称 
        "fileManagerListPath": "/ueditor/php/upload/file/",  # 指定要列出文件的目录 
        "fileManagerUrlPrefix": "",  # 文件访问路径前缀 
        "fileManagerListSize": 20,  # 每次列出文件数量 
        "fileManagerAllowFiles": [
            ".png", ".jpg", ".jpeg", ".gif", ".bmp",
            ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
            ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
            ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
            ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml"
        ]  # 列出的文件类型 

    }
    if action == "config":
        return defaultConfig


def find_or_create_file(session, content, prefix, filename=None):
    md5 = md5_bytes(content)
    size = len(content)
    file = filetype.guess(content)
    db_model = CrudFunctionAnnexe.init().first(session=session, where=[("md5", md5), ("prefix", prefix)])
    if db_model is None:
        path = os.path.join(UPLOAD_DIR, prefix, os.path.split(file.mime)[0], "{}.{}".format(md5, file.extension))
        bool_res = write_file(path, content)
        if bool_res:
            try:
                from PIL import Image
                img = Image.open(path)
                width, height = img.size
            except:
                width, height = (0, 0)
            filename = filename or "{}.{}".format(md5, file.extension)
            CrudFunctionAnnexe.init().store(
                session=session, item=SchemasFunctionAnnexeStoreUpdate(
                    prefix=prefix, filename=filename, content_type=file.mime,
                    md5=md5, path=path, size=size, width=width, height=height
                )
            )
            db_model = CrudFunctionAnnexe.init().first(session=session, where=("md5", md5))
    return db_model


@route('/_M_.ueditor', module=name, router=router, methods=['post'])
async def store_ueditor_model(action: str, request: Request, file: Optional[UploadFile] = File(default=None), source: list = Form(), session: Session = Depends(_session),
                              auth: SchemasFunctionScopes = Security(auth_user, scopes=role_scopes + ["%s.store" % name])):
    if action == "uploadimage":
        content = await file.read()
        db_model = find_or_create_file(session=session, content=content, prefix=auth.prefix, filename=file.filename)
        return SchemasUpLoadFileResponse(url=db_model.preview_path, type=db_model.content_type, size=db_model.size, original=db_model.filename, title=db_model.filename)
    elif action == "catchimage":
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }
        catcher = []
        for _source in source:
            r = requests.get(_source, headers=headers, stream=True)
            if r.status_code == 200:
                content = r.content
                db_model = find_or_create_file(session=session, content=content, prefix=auth.prefix)
                state = "SUCCESS"
                url = db_model.preview_path
            else:
                state = "ERROR_UNKNOWN"
                url = ""
            catcher.append({
                "state": state,
                "url": url,
                "source": _source
            })
        state = "SUCCESS" if bool(len(catcher)) else "ERROR"
        return SchemasUpLoadFileResponse(state=state, list=catcher)


@route('/_M_.content.file', module=name, router=router, methods=['post'])
async def content_file_model(path: str = Form(), file: UploadFile = File(...)):
    """
    留给模板用
    :param path:
    :param file:
    :return:
    """
    content = await file.read()
    bool_res = write_file(path=os.path.join(UPLOAD_DIR, "template", path), content=content)
    return Schemas() if bool_res else SchemasError()
