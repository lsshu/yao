import os
import json
import requests
from datetime import datetime
from urllib.parse import quote

base_attempts = 3


class MP(object):
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
            try:
                from config import MP_CACHE_FILE
            except:
                MP_CACHE_FILE = os.path.join(os.path.dirname(__file__), "mp.token.%s" % app_id)
            self.cache_file = MP_CACHE_FILE

    def message(self, openid=None, template_id=None, url=None, miniprogram=None, client_msg_id=None, data={}, attempts=0):
        """
        发送订阅信息
        Args:
            openid:
            template_id:
            url:
            miniprogram:
            client_msg_id:
            data:
            attempts:

        Returns:

        """
        res = requests.post("https://api.weixin.qq.com/cgi-bin/message/template/send", params={
            "access_token": self.get_token()
        }, json={
            "touser": openid,
            "template_id": template_id,
            "url": url,
            "miniprogram": miniprogram,
            "client_msg_id": client_msg_id,
            "data": data
        }
                            )
        if res.status_code == 200:
            return res.json()
        else:
            if attempts < base_attempts:
                return self.message(openid=openid, template_id=template_id, url=url, miniprogram=miniprogram, client_msg_id=client_msg_id, data=data, attempts=attempts + 1)
            else:
                return {}

    def code_to_auto_info(self, code, attempts=0):
        """
        code 换取授权信息
        Args:
            code:
            attempts:

        Returns:

        """
        res = requests.get("https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code", params={
            "grant_type": "authorization_code", "appid": self.app_id, "secret": self.app_secret, "code": code
        })
        if res.status_code == 200:
            data = res.json()
            return self.__get_auth_info(access_token=data.get("access_token"), openid=data.get("openid"))
        else:
            if attempts < base_attempts:
                return self.code_to_auto_info(code=code, attempts=attempts + 1)
            else:
                return {}

    def __get_auth_info(self, access_token, openid, attempts=0):
        """
        获取用户信息
        Args:
            access_token:
            openid:
            attempts:

        Returns:

        """
        res = requests.get("https://api.weixin.qq.com/sns/userinfo", params={
            "access_token": access_token, "openid": openid, "lang": "zh_CN"
        })
        if res.status_code == 200:
            return res.json()
        else:
            if attempts < base_attempts:
                return self.__get_auth_info(access_token=access_token, openid=openid, attempts=attempts + 1)
            else:
                return {}

    def code_to_openid(self, code, attempts=0):
        """
        code 换取授权信息
        Args:
            code:
            attempts:

        Returns:

        """
        res = requests.get("https://api.weixin.qq.com/sns/oauth2/access_token", params={
            "grant_type": "authorization_code", "appid": self.app_id, "secret": self.app_secret, "code": code
        })
        if res.status_code == 200:
            return res.json()
        else:
            if attempts < base_attempts:
                return self.code_to_openid(code=code, attempts=attempts + 1)
            else:
                return {}

    def get_or_to_auth_url(self, redirect_uri, scope="snsapi_base", state="L", fastapi_return=False):
        """
        获取或者到授权地址
        Args:
            redirect_uri:
            scope: snsapi_base | snsapi_userinfo
            state:
            fastapi_return:
        Returns:

        """
        redirect_uri = quote(redirect_uri)
        url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect" % (
            self.app_id, redirect_uri, scope, state)
        if fastapi_return:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=url)
        return url

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

#
# if __name__ == '__main__':
#     from config import MPAPPID, MPAPPSECRET
#
#     mp = MP(app_id=MPAPPID, app_secret=MPAPPSECRET)
#     print(mp.message(openid="o9vB96AmVEZCLO09jPaplvvRDlok", template_id="8BNzzuBzXd_ttcr2KHAbDEuJLyQ5IVKXYR1YiRLJ2Sk", data={
#         "thing2": {
#             "value": "公司高抛"
#         },
#         "thing3": {
#             "value": "软件园43号楼"
#         },
#         "time5": {
#             "value": "2022年12月27日 13:48:43"
#         },
#     }))
