from yao.crud import Operation
from yao.function.model import ModelFunctionDepartments as Model


class CrudFunctionDepartment(Operation):
    """用户表操作"""
    model_class = Model
