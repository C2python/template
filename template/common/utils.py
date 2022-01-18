# -*- coding: utf-8 -*-

import string
import uuid

def trim_head_tail(str):
    return str.strip(string.ascii_letters)

def generate_uuid():
    return str(uuid.uuid1())

def cst_err(code,message,requestid=None):
    return {
        "Response": {
            "Error": {
                "Code": code,
                "Message": message
            },
        "RequestId":  generate_uuid if requestid is None else requestid
        }

    }