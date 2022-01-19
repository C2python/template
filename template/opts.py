# -*- coding: utf-8 -*-

from oslo_config import cfg


api_opts = [
    cfg.StrOpt('paste_config',
                default="api-paste.ini",
                help='Path to API Paste configuration.'),
    cfg.StrOpt('app_test',
                default="tempalet",
                help='APP Cfg Test.'),
]

auth_opts = [
    cfg.BoolOpt('auth_enable',
                default=True,
                help='Enable/Diable auth.'),
    cfg.StrOpt('tauth_url',
                default="http://tauth.example.org",
                help='Tenant Cookie Verify.'),
    cfg.StrOpt('oauth_url',
                default="http://oauth.example.org",
                help='Operator Auth Verfiy.'), 
]

processor_opts = [
    cfg.StrOpt('db_url',
                required=True,
                help='DB Url.'), 
    cfg.StrOpt('zk_url',
                required=True,
                help='Zookeeper Url.'),
    cfg.StrOpt('zk_user',
                help='Zookeeper User.'),
    cfg.StrOpt('zk_password',
                help='Zookeeper Password.'),
    cfg.IntOpt('zk_timeout',
                default=10,
                help='Zookeeper Password.'),
    cfg.IntOpt('template_polling_interval',
                default=1800,
                help='Template Polling Interval(s).'),
    cfg.IntOpt('workers',
                default=3,
                help='Domain Polling Interval(s)..'),
    cfg.StrOpt('backend',
                default='zk,redis',
                help='backend.'),
]

def list_opts():
    return [
        ('api',api_opts),
        ('auth',auth_opts),
        ('processor',processor_opts)
    ]