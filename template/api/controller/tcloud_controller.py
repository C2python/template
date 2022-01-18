# -*- coding: utf-8 -*-

import pecan
import json
import uuid
import time
import random
import threading

from cachetools import TTLCache
from datetime import datetime, timedelta
from pecan import expose, redirect, Response
from oslo_log import log
from pecan import rest
from template.api.auth import _request
from template.exceptions import tmp_except
from template.common import utils

LOG = log.getLogger(__name__)

class TController(object):
    
    def __init__(self):
        self._cache = TTLCache(maxsize=128, ttl=timedelta(minutes=10), timer=datetime.now)
        self._lock = threading.Lock()

    @expose(generic=True, template='json')
    def index(self):
        return {
            "version": "2010-10-11",
            "links": [
                {"rel": "self",
                 "href": pecan.request.application_url}
            ] 
        }
    
    def _handle_actions(self,conf,**kwargs):

        cookies = pecan.request.cookies
        body = json.loads(pecan.request.body.decode(encoding="utf-8"))
        resp = {'result': 'successed',
                'operator': 'tcloud'}
        return resp

    # HTTP POST /
    @index.when(method='POST', template='json')
    def index_POST(self, **kw):
        LOG.info("Post Method Rec")
        conf = pecan.request.cfg
        return self._handle_actions(conf,**kw)