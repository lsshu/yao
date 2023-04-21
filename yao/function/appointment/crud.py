from yao.crud import Operation
from yao.function.model import ModelFunctionAppointments, ModelFunctionPermissions
from yao.function.appointment.schema import SchemasFunctionAppointmentStoreUpdate


class CrudFunctionAppointment(Operation):
    """用户表操作"""
    model_class = ModelFunctionAppointments
    relationships = {
        "permissions": ModelFunctionPermissions
    }

    def store(self, session, item: SchemasFunctionAppointmentStoreUpdate = None, **kwargs):
        if item.permissions:
            _relation = Operation.init(model_class=ModelFunctionPermissions).get(session=session, where=("uuid", 'in_', item.permissions))
            item.scopes = " ".join([relation.scope for relation in _relation])
        return super().store(session=session, item=item, **kwargs)

    def update(self, session, item: SchemasFunctionAppointmentStoreUpdate = None, **kwargs):
        if item.permissions:
            _relation = Operation.init(model_class=ModelFunctionPermissions).get(session=session, where=("uuid", 'in_', item.permissions))
            item.scopes = " ".join([relation.scope for relation in _relation])
        return super().update(session=session, item=item, **kwargs)
