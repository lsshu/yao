from yao.crud import Operation
from yao.function.model import ModelFunctionQueues as Models


class Crud(Operation):
    """操作"""
    model_class = Models
