import importlib
from datetime import datetime, timedelta

from config import DEFAULT_FUNCTION_COMPANY, OAUTH_ADMIN_USERS
from yao.function.user.crud import CrudFunctionUser

from yao.function.user.schema import SchemasFunctionScopes

from yao.function.queue.type import queue_function_data
from yao.function.queue.crud import Crud as QueueCrud
from yao.function.queue.schema import SchemasStoreUpdate as QueueSchemasStoreUpdate, SchemasQueueAuth
from yao.db import session as _session


def add_queue_function(module, name, data=None, auth: SchemasFunctionScopes = None, priority=5, unique_key=None, scope=None) -> bool:
    """
    添加队列数据
    :param module:
    :param name:
    :param data:
    :param auth:
    :param priority:
    :param unique_key:
    :param scope:
    :return:
    """
    try:
        session = next(_session())
        if not auth:
            prefix_name = DEFAULT_FUNCTION_COMPANY.get("prefix_name", "yao")
            user_name = "%s@%s" % (prefix_name, OAUTH_ADMIN_USERS.keys()[0] if len(OAUTH_ADMIN_USERS) > 1 else "admin")
            user = CrudFunctionUser.init().first(session=session, where=[("username", user_name)])
            auth = SchemasFunctionScopes(user=user, prefix=user.prefix)
        data = queue_function_data(module, name, data, auth)
        item = QueueSchemasStoreUpdate(
            prefix=auth.prefix, username=auth.user.username, priority=priority,
            scope=scope, data=data, key=unique_key, queue_status=0, retry=0
        )
        if unique_key:
            QueueCrud.init().find_or_store_model(session=session, where=[("key", unique_key), ("queue_status", "in", [0, 3])], item=item, close=True)
        else:
            QueueCrud.init().store(session=session, item=item, close=True)
        return True
    except:
        return False


# def digestion_queue(where=[]):
#     """
#     消化队列
#     :return:
#     """
#     session = next(_session())
#     created_at = datetime.now() + timedelta(days=-7)
#     queues = QueueCrud.init().get(session=session, where=[("queue_status", "in", [0, 2]), ("retry", "<", 5), ("created_at", ">", created_at)] + where, order=[("priority", "asc")])
#     for queue in queues:
#         data = queue.data or {}
#         module_name = data.get("module", None)
#         metaclass = importlib.import_module(module_name)
#         if metaclass:
#             if data.get("type") == "function":
#                 function_name = data.get("function_name")
#                 function_data = data.get("function_data", {})
#                 fuc = getattr(metaclass, function_name)
#                 start_at = datetime.now()
#                 QueueCrud.init().update(
#                     session=session, uuid=queue.uuid, event=True, exclude_unset=True,
#                     item=QueueSchemasStoreUpdate(start_at=start_at, stop_at=None, queue_status=3, progress=None, progress_text=None)
#                 )
#                 try:
#                     auth = function_data.get("auth", {})
#                     auth_item = SchemasQueueAuth(**auth)
#                     if len(auth) > 0:
#                         del function_data["auth"]
#                     fuc(queue=queue.uuid, auth=auth_item, **function_data)
#                     queue_status = 1
#                     progress = "100%"
#                 except:
#                     queue_status = 2
#                     progress = None
#                 item = QueueSchemasStoreUpdate(queue_status=queue_status, progress=progress, stop_at=datetime.now(), retry=queue.retry + 1)
#                 QueueCrud.init().update(session=session, uuid=queue.uuid, item=item, event=True, exclude_unset=True)
#     session.close()


def digestion_queue(where=[]):
    """
    消化队列
    :return:
    """
    while True:
        session = next(_session())
        created_at = datetime.now() + timedelta(days=-7)
        queue = QueueCrud.init().first(
            session=session,
            where=[("queue_status", "in", [0, 2]), ("retry", "<", 5), ("created_at", ">", created_at)] + where,
            order=[("priority", "asc")]
        )
        if not queue:
            break
        else:
            data = queue.data or {}
            module_name = data.get("module", None)
            metaclass = importlib.import_module(module_name)
            if metaclass:
                if data.get("type") == "function":
                    function_name = data.get("function_name")
                    function_data = data.get("function_data", {})
                    fuc = getattr(metaclass, function_name)
                    start_at = datetime.now()
                    QueueCrud.init().update(
                        session=session, uuid=queue.uuid, event=True, exclude_unset=True, close=False,
                        item=QueueSchemasStoreUpdate(start_at=start_at, stop_at=None, queue_status=3, progress=None, progress_text=None)
                    )
                    try:
                        auth = function_data.get("auth", {})
                        auth_item = SchemasQueueAuth(**auth)
                        if len(auth) > 0:
                            del function_data["auth"]
                        fuc(queue=queue.uuid, auth=auth_item, **function_data)
                        queue_status = 1
                        progress = "100%"
                    except:
                        queue_status = 2
                        progress = None
                    item = QueueSchemasStoreUpdate(queue_status=queue_status, progress=progress, stop_at=datetime.now(), retry=queue.retry + 1)
                    QueueCrud.init().update(session=session, uuid=queue.uuid, item=item, event=True, close=False, exclude_unset=True)
        try:
            session.close()
        except:
            pass


def progress_queue(uuid, progress=None, progress_text=None):
    """
    更新进度
    :param uuid:
    :param progress:
    :param progress_text:
    :return:
    """
    try:
        if uuid:
            session = next(_session())
            QueueCrud.init().update(session=session, uuid=uuid, item=QueueSchemasStoreUpdate(progress=progress, progress_text=progress_text), event=True, exclude_unset=True)
            session.close()
    except:
        pass


# if __name__ == '__main__':
#     digestion_queue()
