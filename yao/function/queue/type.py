def queue_function_data(module, function_name, function_data=None, auth=None):
    """
    队列方法 需要的参数
    :param module:
    :param function_name:
    :param function_data:
    :param auth:
    :return:
    """
    if auth and type(function_data) is dict:
        function_data.update({"auth": {"prefix": auth.prefix, "username": auth.user.username}})
    return {
        "module": module,
        "type": "function",
        "function_name": function_name,
        "function_data": function_data if function_data else {}
    }
