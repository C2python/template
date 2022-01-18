# -*- coding: utf-8 -*-

import requests
import json

from oslo_log import log
from template.exceptions import tmp_except

LOG = log.getLogger(__name__)

test = 1

class Req(object):
    # 目前默认是http
    _scheme = "http"
    '''
    _method={
        "POST": self._post,
        "GET": self._get,
        "DELETE": self._delete
    }
    '''
    def __init__(self,url):
        self._endpoint = url
        self._method={
            "POST": self._post,
            "GET": self._get,
            "DELETE": self._delete
        }

    def _get_endpoint(self):
        if self._scheme == "https":
            tcloud_url = "https://" + self._endpoint
        else:
            tcloud_url = "http://" + self._endpoint
        return tcloud_url

    def _post(self,**kwargs):
        body = kwargs.get("body",None)
        headers = kwargs.get("headers",None)
        cookie = kwargs.get("cookies",None)
        para = kwargs.get("para",None)
        
        try:
            resp = requests.post(self._get_endpoint(),params=para,data=json.dumps(body),headers=headers,cookies=cookie)
        except requests.ConnectTimeout as err:
            LOG.error("Connection Timeout Error ,ERR: %s" % err)
            raise tmp_except.TemplateInternalException(tmp_except.InternalError,"内部错误")
        except reuqests.ConnectionError as err:
            LOG.error("Connection Error ,ERR: %s" % err)
            raise tmp_except.TemplateInternalException(tmp_except.InternalError,"内部错误")
        except:
            LOG.error("Connection Unknown Error.")
            raise tmp_except.TemplateInternalException(tmp_except.InternalError,"内部错误")
        
        if resp.status_code != 200:
            raise tmp_except.TemplateInternalException(tmp_except.InternalError,"内部错误")

        resp_content = resp.content.decode("utf-8")
        resp_json = json.loads(resp_content)

        return resp_json
            

    def _get(self,**kwargs):
        """
        To do
        """
        pass

    def _delete(self,**kwargs):
        """
        To do
        """
        pass

    def make_request(self,method,**kwargs):
        resp = self._method[method](**kwargs)
        return resp

def send(method,url=None,**kwargs):
    """
    Call http request
    """
    global test
    if test == 1:
        return {'ret':0}
    rq = Req(url)
    try:
        rsp = rq.make_request(method,**kwargs)
    except tmp_except.TemplateInternalException as err:
        raise

    return rsp