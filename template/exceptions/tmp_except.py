# -*- coding: utf-8 -*-

InvalidLoginStatus = 2001
InvalidParameter = 2003
InternalError = 2002
MissingParameter = 2004
UnauthorizedOperation = 2005

error_code = {
    2001: "登录态过期",
    2002: "内部错误",
    2003: "参数错误",
    2004: "缺少参数",
    2005: "无权限"

}

class TemplateErrorException(Exception):
    '''处理内部异常'''
    def __init__(self,code,message):
        self.code = code
        self.message = message
    def __str__(self):
        return self.message

class TemplateInternalException(Exception):
    '''处理内部异常'''
    def __init__(self,code,message):
        self.code = code
        self.message = message
    def __str__(self):
        return self.message

class ExtensionLoadError(Exception):
    """
    Error of loading provider driver.
    """
    def __init__(self,msg=None):
        self.msg = msg