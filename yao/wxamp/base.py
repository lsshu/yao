import os
import json
import requests
from datetime import datetime

base_attempts = 3


class AMP(object):
    app_id = None
    app_secret = None
    cache_file = None
    __errors = []

    def __init__(self, app_id=None, app_secret=None, cache_file=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.__errors = []
        if cache_file:
            self.cache_file = cache_file
        else:
            self.cache_file = os.path.join(os.path.dirname(__file__), "token.%s" % app_id)

    def code2session(self, js_code, attempts=0):
        """小程序登录"""
        res = requests.get("https://api.weixin.qq.com/sns/jscode2session", params={
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": js_code,
            "grant_type": "authorization_code",
        })
        if res.status_code == 200:
            return res.json()
        else:
            if attempts < base_attempts:
                return self.code2session(js_code, attempts=attempts + 1)
            else:
                return {}

    def message(self, openid=None, template_id=None, page=None, state="formal", lang="zh_CN", data={}, attempts=0):
        """
        发送订阅信息
        Args:
            openid:
            template_id:
            page:
            state:
            lang:
            data:
            attempts:

        Returns:
        """
        res = requests.post("https://api.weixin.qq.com/cgi-bin/message/subscribe/send", params={
            "access_token": self.get_token()
        }, json={
            "touser": openid,
            "template_id": template_id,
            "page": page,
            "miniprogram_state": state,
            "lang": lang,
            "data": data
        })
        if res.status_code == 200:
            return res.json()
        else:
            if attempts < base_attempts:
                return self.message(openid=openid, template_id=template_id, page=page, state=state, lang=lang, data=data, attempts=attempts + 1)
            else:
                return {}

    def get_token(self):
        cache_content = self.__get_file_content_or_create_file(self.cache_file)
        if "access_token" in cache_content and "expires_time" in cache_content and cache_content.get("expires_time") > datetime.now().timestamp():
            return cache_content.get("access_token")
        else:
            token = self.__get_token()
            token.update({
                "expires_time": datetime.now().timestamp() + token.get("expires_in", 0)
            })
            self.__create_file(self.cache_file, content=json.dumps(token), mode="w")
            return token.get("access_token")

    def get_generate_scheme(self, path=None, query=None, env_version="release", is_expire=True, expire_type=1, expire_interval=1, attempts=0):
        data = {
            "is_expire": is_expire,
            "expire_type": expire_type,
            "expire_interval": expire_interval
        }
        if path:
            data.update({
                "jump_wxa": {
                    "path": path,
                    "query": query,
                    "env_version": env_version
                }
            })
        res = requests.post("https://api.weixin.qq.com/wxa/generatescheme", params={
            "access_token": self.get_token()
        }, json=data)
        if res.status_code == 200:
            res_data = res.json()
            # print(res_data)
            if res_data.get("errcode") == 0:
                return res_data.get("openlink")
            # elif res_data.get("errcode") == 40001:
            #     self.__create_file(path, content="{}", mode="w")
            #     if attempts < base_attempts:
            #         return self.get_generate_scheme(path=path, query=query, env_version=env_version, is_expire=is_expire, expire_type=expire_type, expire_interval=expire_interval,
            #                                         attempts=attempts + 1)
            else:
                self.error("获取scheme码", res_data)
                return False
        else:
            if attempts < base_attempts:
                return self.get_generate_scheme(path=path, query=query, env_version=env_version, is_expire=is_expire, expire_type=expire_type, expire_interval=expire_interval,
                                                attempts=attempts + 1)
            else:
                return False

    def get_generate_url_link(self, path=None, query=None, env_version="release", is_expire=True, expire_type=1, expire_interval=1, cloud_base=None, attempts=0):
        data = {
            "path": path,
            "query": query,
            "is_expire": is_expire,
            "expire_type": expire_type,
            "expire_interval": expire_interval,
            "env_version": env_version
        }

        if cloud_base:
            data.update({
                "cloud_base": cloud_base
            })
        res = requests.post("https://api.weixin.qq.com/wxa/generate_urllink", params={
            "access_token": self.get_token()
        }, json=data)
        if res.status_code == 200:
            res_data = res.json()
            if res_data.get("errcode") == 0:
                return res_data.get("url_link")
            else:
                self.error("获取URLLink", res_data)
                return False
        else:
            if attempts < base_attempts:
                return self.get_generate_url_link(path=path, query=query, env_version=env_version, is_expire=is_expire, expire_type=expire_type, expire_interval=expire_interval,
                                                  cloud_base=cloud_base, attempts=attempts + 1)
            else:
                return False

    def __get_token(self, attempts=0):
        res = requests.get("https://api.weixin.qq.com/cgi-bin/token", params={
            "grant_type": "client_credential", "appid": self.app_id, "secret": self.app_secret
        })
        if res.status_code == 200:
            return res.json()
        else:
            if attempts < base_attempts:
                return self.__get_token(attempts=attempts + 1)
            else:
                return {}

    def __create_file(self, path, content=None, mode="wb", **kwargs):
        path_dir = os.path.dirname(path)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        if not os.path.isdir(path):
            with open(path, mode, **kwargs) as f:
                f.write(content)
            return True
        return False

    def __get_file_content(self, path, mode="rb", **kwargs):
        """获取文件内容"""
        if os.path.isfile(path):
            with open(path, mode, **kwargs) as f:
                return f.read()
        return bytes()

    def __get_file_content_or_create_file(self, path, read_mode="r", write_mode="w"):
        if not os.path.exists(self.cache_file):
            self.__create_file(path, content="{}", mode=write_mode)
            return dict()
        else:
            bytes_content = self.__get_file_content(path, mode=read_mode)
            return json.loads(bytes_content)

    def error(self, text=None, response=None):
        """
        设置或者获取错误
        :param text:
        :param response:
        :return:
        """
        if text is None and response is None:
            return self.__errors
        self.__errors.append({"text": text, "response": response})


if __name__ == '__main__':
    from config import PROGRAMAPPID, PROGRAMAPPSECRET

    amp = AMP(PROGRAMAPPID, PROGRAMAPPSECRET)
    token = amp.get_generate_scheme(path="/pages/news/sale", query="2a9926ec30694321b2e8b53aced97fc6")
    print(token)