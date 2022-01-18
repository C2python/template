# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import webob
import json
import random
import time

from oslo_log import log
from template.api.auth import _request
from template.common import utils
from template.exceptions import tmp_except

LOG = log.getLogger(__name__)

"""
Cloud Admin login status verify:
URL Method:


"""

class OAuthProtocol(object):

    def __init__(self, app, conf):
        global APPCONFIGS
        LOG.info('Starting auth_token middleware')
        self._app = app
        #self._conf = APPCONFIGS[conf["configkey"]]
        self._conf = json.loads(conf['auth'])

    def _make_cst(self):
        
        body = {
            'test': 'Test'
        }

        return body

    @webob.dec.wsgify
    def __call__(self,req):
        """Handle incoming request."""
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self._app)
        return self.process_response(response)
    
    def process_request(self,request):
        """Process request.

        Evaluate the headers in a request and attempt to authenticate the
        request. If authenticated then additional headers are added to the
        request for use by applications. If not authenticated the request will
        be rejected or marked unauthenticated depending on configuration.
        """
        request_id = utils.generate_uuid()
        LOG.info("Start Authentication.")
        try:
            cookies = request.cookies
        except KeyError:
            LOG.info("Auth Failed. No Cookies")
            msg = utils.cst_err(tmp_except.InvalidLoginStatus,"Cookie Missing.",request_id)
            raise webob.exc.HTTPUnauthorized(
                body=json.dumps(msg,ensure_ascii=False),
                charset='UTF-8',
                content_type='application/json')

        ocloud_url = self._conf['oauth_url']

        body = self._make_cst()
        kwargs = dict(body=body)
        kwargs["cookies"] = cookies

        if not self._conf['auth_enable']:
            return

        try:
            resp = _request.send("POST",url=ocloud_url,**kwargs)
        except tmp_except.TemplateInternalException as err:
            LOG.error("Cannot Authenticate Cookie Due to Internal Error")
            msg = utils.cst_err(err.code,err.message,request_id)
            raise webob.exc.HTTPInternalServerError(
                body=json.dumps(msg,ensure_ascii=False),
                charset='UTF-8',
                content_type='application/json')

        if resp["ret"] != 0:
            LOG.info("Cookie is expired, cookie: %s" % request.cookies)
            msg = utils.cst_err(tmp_except.InvalidLoginStatus,"登录态过期",request_id)
            raise webob.exc.HTTPUnauthorized(
                body=json.dumps(msg,ensure_ascii=False),
                charset='UTF-8',
                content_type='application/json')
        
        LOG.info("Verified Succeed.")

    def process_response(self,response):
        """Process Response.

        Reserved to do some special response
        Example: 
        if response.status_int == 401:
            response.headers.extend(self._reject_auth_headers)
        """

        return response

def filter_factory(global_conf, **local_conf):
    """Return a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_filter(app):
        return OAuthProtocol(app, conf)
    return auth_filter