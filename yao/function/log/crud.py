from yao.crud import Operation
from yao.function.model import ModelFunctionLogs as Model


class CrudFunctionLog(Operation):
    """表操作"""
    model_class = Model
