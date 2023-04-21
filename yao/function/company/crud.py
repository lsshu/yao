from yao.crud import Operation
from yao.function.model import ModelFunctionCompanies


class CrudFunctionCompany(Operation):
    """公司表操作"""
    model_class = ModelFunctionCompanies
