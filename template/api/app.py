# -*- coding: utf-8 -*-


import os
import uuid
import pecan
import json
import pkg_resources
from paste import deploy
from oslo_config import cfg
from oslo_log import log

from template.api import hooks
from template import service

LOG = log.getLogger(__name__)

# NOTE(sileht): pastedeploy uses ConfigParser to handle
# global_conf, since python 3 ConfigParser doesn't
# allow storing object as config value, only strings are
# permit, so to be able to pass an object created before paste load
# the app, we store them into a global var. But the each loaded app
# store it's configuration in unique key to be concurrency safe.
global APPCONFIGS
APPCONFIGS = {}

def setup_app(root, conf):
    app_hooks = [hooks.ConfigHook(conf),
                 hooks.TranslationHook()]
    return pecan.make_app(
        root,
        hooks=app_hooks,
        guess_content_type_from_ext=False
    )

def load_app(conf):
    global APPCONFIGS

    # Build the WSGI app
    cfg_path = conf.api.paste_config
    if not os.path.isabs(cfg_path):
        cfg_path = conf.find_file(cfg_path)

    if cfg_path is None or not os.path.exists(cfg_path):
        LOG.debug("No api-paste configuration file found! Using default.")
        cfg_path = os.path.abspath(pkg_resources.resource_filename(
            __name__, "api-paste.ini"))

    LOG.info("Test cfg_path: %s", cfg_path)
    
    config = dict(conf=conf)
    configkey = str(uuid.uuid4())
    APPCONFIGS[configkey] = config


    # 添加银联相关配置
    pl_conf = {
                'tauth_url': conf.auth.tauth_url, 
                'auth_enable': conf.auth.auth_enable
            }

    if conf.auth.auth_enable:
        pro_name = "template+basic"
    else:
        pro_name = "template+noauth"

    global_conf = {
        'configkey': configkey,
        'auth': json.dumps(pl_conf)}

    LOG.info("WSGI config used: %s", cfg_path)
    return deploy.loadapp("config:" + cfg_path,
                          name=pro_name,
                          global_conf=global_conf)

def app_factory(global_config, **local_conf):
    global APPCONFIGS
    appconfig = APPCONFIGS.get(global_config.get('configkey'))
    return setup_app(root=local_conf.get('root'), **appconfig)

def build_wsgi_app(argv=None):
    return load_app(service.prepare_service(argv=argv))