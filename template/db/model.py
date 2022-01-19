# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base

import json

Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True)
    uin = Column(String(64))
    deleted = Column(Integer)  # 是否删除
    create_time = Column(DateTime)  # 创建时间
    update_time = Column(DateTime,onupdate=True)  # 更新时间
    delete_time = Column(DateTime,nullable=True)  # 删除时间

    def __repr__(self):
        return json.dumps({
            'id': self.id,
            'uin': self.uin,
            'deleted': self.deleted,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'delete_time': self.delete_time,
        },ensure_ascii=False)