# -*- coding: utf-8 -*-

import sys

from oslo_log import log
from template import opts
from oslo_config import cfg

def prepare_service(conf=None,argv=None,config_files=None):
    if conf is None:
        conf = cfg.ConfigOpts()
    for group,options in opts.list_opts():
        conf.register_opts(list(options),
                            group=None if group == 'DEFAULT' else group)
    #conf.register_cli_opts(opts._cli_options)
    log.register_options(conf)
    if argv is None:
        argv = sys.argv
    conf(argv[1:],project='template',validate_default_values=True,
        default_config_files=config_files)
    log.setup(conf,'template')
    return conf