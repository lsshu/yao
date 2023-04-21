from yao.crud import Operation
from yao.function.model import ModelFunctionPermissions


class CrudFunctionPermission(Operation):
    """权限表操作"""
    model_class = ModelFunctionPermissions
