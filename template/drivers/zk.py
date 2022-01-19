# -*- coding: utf-8 -*-

from oslo_log import log
from template import drivers

LOG = log.getLogger(__name__)

class ZookCli(drivers.DriverBase):
    DRIVER_NAME = 'ZOOKEEPER'
    
    def __init__(self,conf):
        print("Init")
        LOG.info("Load driver: %s." % self.DRIVER_NAME)
        super(ZookCli,self).__init__(conf)
    
    def test(self):
        LOG.info('Run test, driver: %s' % self.DRIVER_NAME)
    
    def get(self):
        pass