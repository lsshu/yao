from abc import ABCMeta
from typing import Union, List, Tuple, Optional

from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from pydantic import BaseModel


class Operation(object, metaclass=ABCMeta):
    """
    模型类
    """
    model_class = None
    model_pk = "id"
    relationships: dict = {}  # 多对多时使用
    relationship_pk: str = "uuid"  # 多对多传来的值对应的字段　　　
    relations: dict = {}  # 关联表 用于join等
    instance = None
    query = None

    limit = None
    page = None
    order = None

    def __init__(self, model_class=None, model_pk=None):
        """
        实例化对象
        :param model_class:
        :param model_pk:
        """
        if model_class:
            """设置模型类"""
            self.model_class = model_class
        if model_pk:
            """设置主銉"""
            self.model_pk = model_pk

    @classmethod
    def init(cls, cache=False, **kwargs):
        """
        初始化实例对象
        :param cache:
        :param kwargs:
        :return:
        """
        if not cache or not cls.instance:
            cls.instance = cls(**kwargs)
        return cls.instance

    def __init_query(self, session, field=None):
        """
        初始化查询
        :param field:
        :return:
        """
        self.limit = None
        self.page = None
        self.order = None
        self.query = session.query(field if field else self.model_class)
        return self.query

    def __init_params(self, **kwargs):
        """
        处理kwargs 参数到 params
        :param kwargs:
        :return:
        """
        [(getattr(self, "_%s" % params)(params_value) if hasattr(self, "_%s" % params) else None) for params, params_value in kwargs.items()]
        return self

    def _screen_params(self, params: BaseModel):
        """
        处理screen_params 参数到 params
        :param params:
        :return:
        """
        self.__init_params(**params.dict())
        return self

    def __w_tool(self, model_class, where):
        if where:
            if len(where) == 2:
                return getattr(model_class, where[0]) == where[1]
            elif len(where) == 3:
                if where[1] in ["in"] and type(where[2]) in [list, tuple]:
                    return getattr(getattr(model_class, where[0]), "in_")(where[2])
        return None

    def __filter_query(self, where: Union[list, tuple, None] = None, query=None, model=None):
        """
        过滤数据条件
        :param where:
        :param query:
        :param model:
        :return:
        """
        _query = query if query else self.query
        model_class = model if model else self.model_class
        if bool(where) and (type(where) == tuple or type(where) == list):
            if len(where) == 2:
                """('content', '西')"""
                if where[0][:2] != "__":
                    _query = _query.filter(getattr(model_class, where[0]) == where[1])
                else:
                    """ ("__or", [("a", b), ("c", "in", [1,2])]) """
                    _filters = [self.__w_tool(model_class, fil) for fil in where[1]]
                    if where[0][2:] != "or":
                        _query = _query.filter(or_(*[f for f in _filters if f is not None]))
            elif len(where) == 3:
                if where[1] == "==" or where[1] == "=" or where[1] == "eq":
                    """('content', '==', '西')"""
                    if where[2] != "_#None":
                        _query = _query.filter(getattr(model_class, where[0]) == where[2])
                    else:
                        _query = _query.filter(or_(getattr(model_class, where[0]) == None, getattr(model_class, where[0]) == ""))
                elif where[1] == "!=" or where[1] == "<>" or where[1] == "><" or where[1] == "neq" or where[1] == "ne":
                    """('content', '!=', '西')"""
                    if where[2] != "_#None":
                        _query = _query.filter(getattr(model_class, where[0]) != where[2])
                    else:
                        _query = _query.filter(or_(getattr(model_class, where[0]) != None, getattr(model_class, where[0]) != ""))
                elif where[1] == ">" or where[1] == "gt":
                    """('content', '>', '西')"""
                    _query = _query.filter(getattr(model_class, where[0]) > where[2])
                elif where[1] == ">=" or where[1] == "ge":
                    """('content', '>=', '西')"""
                    _query = _query.filter(getattr(model_class, where[0]) >= where[2])
                elif where[1] == "<" or where[1] == "lt":
                    """('content', '<', '西')"""
                    _query = _query.filter(getattr(model_class, where[0]) < where[2])
                elif where[1] == "<=" or where[1] == "le":
                    """('content', '<=', '西')"""
                    _query = _query.filter(getattr(model_class, where[0]) <= where[2])
                elif where[1] in ["like", "ilike"]:
                    if not where[2] is None:
                        """('content', 'like', '西')"""
                        _query = _query.filter(
                            getattr(getattr(model_class, where[0]), where[1])("%" + where[2] + "%")
                        )
                elif where[1] in ["or"]:
                    if type(where[0]) == tuple or type(where[0]) == list:
                        """(['name','content'], 'or', '西')"""
                        _filters = [(getattr(model_class, fil) == where[2]) for fil in where[0]]
                        _query = _query.filter(or_(*_filters))

                    if type(where[0]) == str and (type(where[2]) == tuple or type(where[2]) == list):
                        """('name', 'or', ['西', '西'])"""
                        _filters = [(getattr(model_class, where[0]) == fil) for fil in where[2]]
                        _query = _query.filter(or_(*_filters))
                elif where[1] in ["or_like", "or_ilike"]:
                    if type(where[0]) == tuple or type(where[0]) == list:
                        """(['name','content'], 'or_like', '西')"""
                        _filters = [(getattr(getattr(model_class, fil), where[1][3:])("%" + where[2] + "%")) for
                                    fil in where[0]]
                        _query = _query.filter(or_(*_filters))
                    if type(where[0]) == str and (type(where[2]) == tuple or type(where[2]) == list):
                        """('name', 'or_like', ['西', '西'])"""
                        _filters = [(getattr(getattr(model_class, where[0]), where[1][3:])("%" + fil + "%")) for
                                    fil in where[2]]
                        _query = _query.filter(or_(*_filters))
                elif where[1] in ["between"] and type(where[2]) in [list, tuple] and len(where[2]) == 2:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), where[1])(where[2][0], where[2][1]))
                elif where[1] in ["datebetween"] and type(where[2]) in [list, tuple] and len(where[2]) == 2:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), 'between')(where[2][0], where[2][1]))
                elif where[1] in ["datetimebetween"] and type(where[2]) in [list, tuple] and len(where[2]) == 2:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), 'between')("%s" % where[2][0], "%s 23:59:59" % where[2][1]))
                elif where[1] in ["in"] and type(where[2]) in [list, tuple]:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), "in_")(where[2]))
                elif where[1] in ["is"]:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), "is_")(where[2]))
                elif where[1] in ["notin"] and type(where[2]) in [list, tuple]:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), "notin_")(where[2]))
                else:
                    _query = _query.filter(getattr(getattr(model_class, where[0]), where[1])(where[2]))
        if not query:
            self.query = _query
        return _query

    def _where(self, where: Optional[Union[List[tuple], List[list], Tuple[tuple], Tuple[list], list, tuple, str]] = None, *args):
        """
        条件集合
        :param where:
        :param args:
        :return:
        """

        if where:
            if (type(where) == list or type(where) == tuple) and type(where[0]) == str:
                where = [where]
            elif type(where) == str:
                where = [(where, *args)]
            [self.__filter_query(where=w) for w in where]

    def _pk(self, pk: int):
        """
        设定查询 主键
        :param pk:
        :return:
        """
        self._where((self.model_pk, pk))

    def _uuid(self, uuid: Union[int, str]):
        """
        设定查询 uuid
        :param uuid:
        :return:
        """
        self._where(("uuid", uuid))

    def _uuids(self, uuids: List[Union[int, str]]):
        """
        设定查询 uuid
        :param uuids:
        :return:
        """
        self._where(("uuid", "in", uuids))

    def _limit(self, limit):
        """
        设置 limit
        :param limit:
        :return:
        """
        self.limit = limit

    def _page(self, page):
        """
        设置 page
        :param page:
        :return:
        """
        self.page = page

    def _order(self, order):
        """
        设置 order
        :param order:
        :return:
        """
        self.order = order

    def _rand(self, limit):
        """
        设置 order
        :param order:
        :return:
        """
        self.limit = limit
        self.query = self.query.order_by(func.rand())

    def _query_limit_page(self):
        if self.limit:
            self.query = self.query.limit(self.limit)
            if self.page:
                self.query = self.query.offset((self.page - 1) * self.limit)

    def _query_order(self):
        if bool(self.order):
            if type(self.order) == tuple or type(self.order) == list:  # 设置排序
                for attr_item in self.order:
                    self.query = self.query.order_by(getattr(getattr(self.model_class, attr_item[0]), attr_item[1])())

    def get(self, session, field=None, close: bool = False, **kwargs):
        """
        获取列表
        :param session:
        :param field:
        :param close:
        :param kwargs:
        :return:
        """
        self.__init_query(session=session, field=field)
        self.__init_params(**kwargs)
        self._query_order()
        self._query_limit_page()
        response = self.query.all()
        close and session.close()
        return response

    def count(self, session, close: bool = False, **kwargs):
        """
        获取列表
        :param session:
        :param close:
        :param kwargs:
        :return:
        """
        self.__init_query(session=session)
        self.__init_params(**kwargs)
        response = self.query.count()
        close and session.close()
        return response

    def paginate(self, session, field=None, limit=None, page=None, order=None, close: bool = False, tree: bool = False, **kwargs):
        """
        分页 操作
        :param session:
        :param field:
        :param limit:
        :param page:
        :param order:
        :param close:
        :param tree:
        :param kwargs:
        :return:
        """
        import math
        total = self.count(session=session, **kwargs)
        if tree:
            items = self.get_tree(session=session, json=False)
            items = [item.get("node") for item in items]
        else:
            items = self.get(session=session, field=field, limit=limit, page=page, order=order, close=close, **kwargs)
        pages = math.ceil(total / self.limit) if type(total) is int and type(self.limit) is int and self.limit != 0 else 1
        return {
            "items": items,  # 当前页的数据列表
            "pages": pages,  # 总页数
            "total": total,  # 总条数
            "page": self.page,  # 当前页
            "limit": self.limit,  # 页条数
        }

    def first(self, session, field=None, close: bool = False, **kwargs):
        """
        获取条件第一个
        :param session:
        :param field:
        :param close:
        :param kwargs:
        :return:
        """
        self.__init_query(session=session, field=field)
        self.__init_params(**kwargs)
        self._query_order()
        response = self.query.first()
        close and session.close()
        return response

    def update(self, session, where=None, item: BaseModel = None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, exclude_unset=True,
               event: bool = False, synchronize_session="evaluate", **kwargs):
        """
        更新数据
        :param session:
        :param where:
        :param item:
        :param data:
        :param commit:
        :param refresh:
        :param close:
        :param exclude_unset:
        :param event:
        :param synchronize_session:
        :param kwargs:
        :return:
        """
        if event:
            obj_item = self.first(session=session, where=where, **kwargs)
            # relationships
            if bool(self.relationships):
                for (relation, relation_class) in self.relationships.items():
                    if hasattr(item, relation) and getattr(item, relation):
                        relation__ = Operation.init(model_class=relation_class)
                        _relation = relation__.get(session=session, where=(relation__.relationship_pk, 'in_', getattr(item, relation)))
                        setattr(item, relation, _relation)
            # relationships
            [setattr(obj_item, k, val) for k, val in item.dict(exclude_unset=exclude_unset).items()]
            commit and session.commit()
            close and session.close()
        else:
            # relationships
            obj_item = None
            if bool(self.relationships):
                for (relation, relation_class) in self.relationships.items():
                    obj_item = obj_item or self.first(session=session, where=where)
                    if hasattr(item, relation) and bool(getattr(item, relation)):

                        relation__ = Operation.init(model_class=relation_class)
                        _relation = relation__.get(session=session, where=(relation__.relationship_pk, 'in_', getattr(item, relation)))
                        setattr(obj_item, relation, _relation)
                    elif not bool(getattr(item, relation)) and relation in item.dict(exclude_unset=exclude_unset):
                        [getattr(obj_item, relation).remove(rela) for rela in list(getattr(obj_item, relation))]  # 出错
                    hasattr(item, relation) and delattr(item, relation)
            # relationships
            self.__init_query(session=session)
            self.__init_params(where=where, **kwargs)
            self.query.update(item.dict(exclude_unset=exclude_unset), synchronize_session=synchronize_session)
            commit and session.commit()
            close and session.close()

    def store(self, session, item: BaseModel = None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, **kwargs):
        """
        创建模型数据
        :param session:
        :param item:
        :param data:
        :param commit:
        :param refresh:
        :param close:
        :param kwargs:
        :return:
        """

        # relationships
        if bool(self.relationships):
            for (relation, relation_class) in self.relationships.items():
                if hasattr(item, relation) and bool(getattr(item, relation)):
                    relation__ = Operation.init(model_class=relation_class)
                    _relation = relation__.get(session=session, where=(relation__.relationship_pk, 'in_', getattr(item, relation)))
                    setattr(item, relation, _relation)
        # relationships

        # 创建实例
        db_item = self.model_class(**item.dict(exclude_unset=True))
        session.add(db_item)
        commit and session.commit()
        refresh and session.refresh(db_item)
        close and session.close()
        return db_item

    def many_store(self, session, items: List[BaseModel], commit: bool = True, close: bool = False, **kwargs):
        """
        批量创建模型数据
        :param session:
        :param items:
        :param commit:
        :param close:
        :param kwargs:
        :return:
        """
        db_items = [self.model_class(**item.dict(exclude_unset=True)) for item in items]
        session.add_all(db_items)
        commit and session.commit()
        close and session.close()
        return db_items

    def delete(self, session, commit: bool = True, close: bool = False, event: bool = False, **kwargs):
        """
        删除多模型数据
        :param session:
        :param commit:
        :param close:
        :param event:
        :param kwargs:
        :return:
        """
        self.__init_query(session=session)
        self.__init_params(**kwargs)
        self._query_order()

        response = [session.delete(u) for u in self.query.all()] if event else self.query.delete()

        commit and session.commit()
        close and session.close()
        return response

    def update_or_store_model(self, session, where=None, item: BaseModel = None, store_item: BaseModel = None, data: dict = None, commit: bool = True, refresh: bool = True,
                              close: bool = False, exclude_unset: bool = True, event: bool = False, update_event: bool = False, **kwargs):
        """
        更新或者创建
        :param session:
        :param where:
        :param item:
        :param store_item:
        :param data:
        :param commit:
        :param refresh:
        :param close:
        :param exclude_unset:
        :param event:
        :param update_event:
        :param kwargs:
        :return:
        """
        instance = self.first(session=session, where=where, **kwargs)
        if instance:
            return self.update(session=session, item=item, data=data, pk=getattr(instance, self.model_pk), exclude_unset=exclude_unset, commit=commit, refresh=refresh, close=close,
                               event=update_event, **kwargs)
        else:
            return self.store(session=session, item=store_item if store_item else item, data=data, commit=commit, refresh=refresh, close=close, event=event, **kwargs)

    def find_or_store_model(self, session, where=None, item: BaseModel = None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, **kwargs):
        """
        查找或者创建
        :param session:
        :param where:
        :param item:
        :param data:
        :param commit:
        :param refresh:
        :param close:
        :param kwargs:
        :return:
        """
        instance = self.first(session=session, where=where, **kwargs)
        if not instance:
            return self.store(session=session, item=item, data=data, commit=commit, refresh=refresh, close=close, **kwargs)
        return instance

    def get_tree(self, session, json=True, json_fields=None, query_function=None, where: Union[list, tuple] = None, **kwargs):
        """
        获取树
        :param session:
        :param json:
        :param json_fields:
        :param query_function:
        :param where:
        :param kwargs:
        :return:
        """

        def query_fun(nodes, _where: Union[list, tuple] = None):
            if _where:
                if (type(_where) == list or type(_where) == tuple) and type(_where[0]) == str:
                    _where = [_where]
                for w in where:
                    nodes = self.__filter_query(where=w, query=nodes)
            return nodes

        return self.model_class.get_tree(session=session, json=json, json_fields=lambda node: node.to_dict() if json is True and not json_fields else json_fields,
                                         query=query_function if query_function else lambda nodes: query_fun(nodes=nodes, _where=where))

    def update_children_uuids(self, **kwargs):
        """
        更新子级uuid
        Args:
            **kwargs:

        Returns:

        """
        objs = self.get(**kwargs)
        for obj in objs:
            ids = []

            def _get_id(obj):
                _ids = [obj.get("node").uuid]
                children = obj.get("children", [])
                if len(children) > 0:
                    for child in children:
                        _ids += _get_id(child)
                return _ids

            for _obj in obj.drilldown_tree():
                ids += _get_id(_obj)
            obj.children_ids = ids
        session = kwargs.get("session")
        commit = kwargs.get("commit", True)
        close = kwargs.get("close", True)
        commit and session.commit()
        close and session.close()
        return True


from time import time


def run_time(func):
    def wrap(*args, **kwargs):
        t1 = time()
        r = func(*args, **kwargs)
        t2 = time()
        print(t2 - t1)
        return r

    return wrap


class LogOperation(Operation):
    @run_time
    def update(self, session, where=None, item: BaseModel = None, data: dict = None, commit: bool = True, refresh: bool = True, close: bool = False, exclude_unset=True,
               event: bool = False, **kwargs):
        return super().update(session=session, where=where, item=item, data=data, commit=commit, refresh=refresh, close=close, exclude_unset=exclude_unset,
                              event=event, **kwargs)
