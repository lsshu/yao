from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, event, Table, JSON
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy_mptt.mixins import BaseNestedSets

from yao.method import plural
from yao.db import Model, Engine

name = __name__[:__name__.rfind(".")].capitalize()

"""职能信息"""
function_name = plural("%s" % name)

"""公司信息"""
function_company_name = plural("%s.company" % name)
function_company_table_name = function_company_name.replace('.', '_')

"""公司部门"""
function_department_name = plural("%s.department" % name)
function_department_table_name = function_department_name.replace('.', '_')

"""员工职位"""
function_appointment_name = plural("%s.appointment" % name)
function_appointment_table_name = function_appointment_name.replace('.', '_')

"""权限信息"""
function_permission_name = plural("%s.permission" % name)
function_permission_table_name = function_permission_name.replace('.', '_')

"""后台账号"""
function_user_name = plural("%s.user" % name)
function_user_table_name = function_user_name.replace('.', '_')

"""附件"""
function_annex_name = plural("%s.annex" % name)
function_annex_table_name = function_annex_name.replace('.', '_')

"""日志"""
function_log_name = plural("%s.log" % name)
function_log_table_name = function_log_name.replace('.', '_')

SYSTEM_PERMISSIONS = [
    {
        "name": "职能信息",
        "scope": function_name,
        "icon": "ElementPlus",
        "children": [
            {"name": "公司信息", "scope": function_company_name, "icon": "Refrigerator"},
            {"name": "公司部门", "scope": function_department_name, "icon": "Help"},
            {"name": "员工职位", "scope": function_appointment_name, "icon": "User"},
            {"name": "权限管理", "scope": function_permission_name, "icon": "KnifeFork", "is_menu": False,
             "action": [{"name": "菜单", "scope": "menus"}, {"name": "树", "scope": "tree"}]},
            {"name": "后台账号", "scope": function_user_name, "icon": "User"},
            {"name": "附件文件", "scope": function_annex_name, "icon": "Folder", "is_menu": False},
            {"name": "操作日志", "scope": function_log_name, "icon": "Document"},
        ]
    }
]


class BaseModel(Model):
    __abstract__ = True
    remarks = Column(String(150), nullable=True, comment="备注")
    sort = Column(Integer, default=999, comment="排序")
    status = Column(Boolean, default=True, comment="状态")


class ModelFunctionCompanies(BaseModel):
    """ 公司信息 """
    __tablename__ = function_company_table_name
    name = Column(String(30), nullable=False, unique=True, comment="公司名称")
    prefix_name = Column(String(20), nullable=False, unique=True, comment="公司前缀")
    contact_name = Column(String(20), nullable=True, comment="联系人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")


class BaseCompanyModel(BaseModel):
    __abstract__ = True

    @declared_attr
    def prefix(self):
        return Column(String(20), ForeignKey('%s.prefix_name' % function_company_table_name, ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False,
                      comment="公司前缀")


class ModelFunctionDepartments(BaseCompanyModel, BaseNestedSets):
    """公司部门"""
    __tablename__ = function_department_table_name
    name = Column(String(40), unique=True, nullable=False, comment="名称")


class ModelFunctionPermissions(BaseModel, BaseNestedSets):
    """ 权限 """
    __tablename__ = function_permission_table_name
    sqlalchemy_mptt_pk_name = "uuid"
    name = Column(String(15), unique=True, nullable=False, comment="名称")
    icon = Column(String(20), nullable=True, comment="ICO")
    scope = Column(String(50), nullable=False, unique=True, comment="Scope")
    path = Column(String(50), nullable=False, comment="Path")
    is_menu = Column(Boolean, default=True, comment="是否为菜单")
    is_action = Column(Boolean, default=True, comment="是否为动作权限")


@event.listens_for(ModelFunctionPermissions.scope, 'set')
def permission_receive_before_insert(target, value: str, old_value, initiator):
    target.path = "/%s" % value.replace('.', '/').lower()


@event.listens_for(ModelFunctionPermissions.scope, 'modified')
def permission_receive_before_insert(target, initiator):
    target.path = "/%s" % target.scope.replace('.', '/').lower()


class ModelFunctionAppointments(BaseCompanyModel):
    """员工职位"""
    __tablename__ = function_appointment_table_name
    department = Column(String(40), ForeignKey('%s.name' % function_department_table_name, ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=True, comment="公司部门")
    name = Column(String(40), unique=True, nullable=False, comment="名称")
    scopes = Column(Text, nullable=False, comment="Scope")
    permissions = relationship(ModelFunctionPermissions, backref='appointments', lazy="joined", secondary=Table(
        "%s_appointment_has_permissions" % function_name,
        Model.metadata,
        Column('per_id', Integer, ForeignKey("%s.id" % function_permission_table_name, ondelete="CASCADE"), primary_key=True, comment="权限"),
        Column('app_id', Integer, ForeignKey("%s.id" % function_appointment_table_name, ondelete="CASCADE"), primary_key=True, comment="职位")
    ))


class ModelFunctionUsers(BaseCompanyModel, BaseNestedSets):
    """登录用户"""
    __tablename__ = function_user_table_name
    username = Column(String(40), nullable=False, unique=True, index=True, comment="名称")
    password = Column(String(128), nullable=False, comment="密码")
    user_phone = Column(String(11), nullable=True, comment="手机")
    available = Column(Boolean, default=1, comment="是否有效")

    permissions = relationship(ModelFunctionPermissions, backref='function_users', secondary=Table(
        "%s_user_has_permissions" % function_name,
        Model.metadata,
        Column('per_id', Integer, ForeignKey("%s.id" % function_permission_table_name, ondelete="CASCADE"), primary_key=True, comment="权限"),
        Column('use_id', Integer, ForeignKey("%s.id" % function_user_table_name, ondelete="CASCADE"), primary_key=True, comment="用户"),
    ))
    appointments = relationship(ModelFunctionAppointments, backref='function_users', secondary=Table(
        "%s_user_has_appointments" % function_name,
        Model.metadata,
        Column('app_id', Integer, ForeignKey("%s.id" % function_appointment_table_name, ondelete="CASCADE"), primary_key=True, comment="职位"),
        Column('use_id', Integer, ForeignKey("%s.id" % function_user_table_name, ondelete="CASCADE"), primary_key=True, comment="用户"),
    ))


class ModelFunctionAnnexes(BaseCompanyModel):
    """ 附件 """
    __tablename__ = function_annex_table_name

    filename = Column(String(50), nullable=False, comment="文件名")
    content_type = Column(String(100), nullable=False, comment="类型")
    path = Column(String(100), nullable=True, comment="路径")
    md5 = Column(String(32), nullable=True, comment="md5", index=True)
    size = Column(Integer, nullable=False, comment="SIZE")
    width = Column(String(100), nullable=True, comment="宽")
    height = Column(String(190), nullable=True, comment="高")

    @property
    def preview_path(self):
        import os
        from config import STATIC_URL
        return os.path.join(STATIC_URL, self.path)


class ModelFunctionLogs(BaseCompanyModel):
    """ 日志 """
    __tablename__ = function_log_table_name
    scope = Column(String(100), nullable=True, comment="scope")
    methods = Column(String(32), nullable=True, comment="methods", index=True)
    data = Column(JSON, nullable=True, comment="Data")
    username = Column(String(32), ForeignKey("%s.username" % function_user_table_name, onupdate="CASCADE", ondelete="CASCADE"), index=True, nullable=True, comment="用户")
