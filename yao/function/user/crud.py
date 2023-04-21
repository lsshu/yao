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
        return super().store(item=item, data=data, commit=commit, refresh=refresh, close=close, **kwargs)

    def update(self, where=None, item=None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, exclude_unset=True, event: bool = False, **kwargs):
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)
        else:
            if hasattr(item, "password"):
                delattr(item, "password")
        return super().update(where=where, item=item, data=data, commit=commit, refresh=refresh, close=close, exclude_unset=exclude_unset, event=event, **kwargs)
