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

def list_opts():
    return [
        ('api',api_opts),
        ('auth',auth_opts)
    ]