from sqlalchemy.orm import Session

from yao.crud import Operation
from yao.helpers import token_get_password_hash
from yao.function.model import ModelFunctionUsers, ModelFunctionPermissions, ModelFunctionAppointments


class CrudFunctionUser(Operation):
    """用户表操作"""
    model_class = ModelFunctionUsers

    relationships = {
        "permissions": ModelFunctionPermissions,
        "appointments": ModelFunctionAppointments
    }

    def store(self, item=None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, **kwargs):
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)
        item.children_ids = [item.username]
        res = super().store(item=item, data=data, commit=commit, refresh=refresh, close=close, **kwargs)
        return res

    def update(self, where=None, item=None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, exclude_unset=True, event: bool = False, **kwargs):
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)
        else:
            if hasattr(item, "password"):
                delattr(item, "password")
        res = super().update(where=where, item=item, data=data, commit=commit, refresh=refresh, close=False, exclude_unset=exclude_unset, event=event, **kwargs)
        self.update_children_ids(close=False, session=kwargs.get("session"))
        return res

    def update_children_ids(self, **kwargs):
        users = self.get(**kwargs)
        for user in users:
            ids = []

            def _get_id(obj):
                _ids = [obj.get("node").username]
                children = obj.get("children", [])
                if len(children) > 0:
                    for child in children:
                        _ids += _get_id(child)
                return _ids

            for _obj in user.drilldown_tree():
                ids += _get_id(_obj)
            user.children_ids = ids
        session = kwargs.get("session")
        commit = kwargs.get("commit", True)
        close = kwargs.get("close", True)
        commit and session.commit()
        close and session.close()
        return True
