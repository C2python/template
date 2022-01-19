# -*- coding: utf-8 -*-

import socket
import threading
import time
import uuid

import cachetools.func
import cotyledon
from cotyledon import oslo_config_glue
from oslo_config import cfg
from oslo_log import log

from template.common import utils
from template import service
from template.common import zk_common

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from template.db.model import TestModel


LOG = log.getLogger(__name__)

class ProcessorRedis(cotyledon.Service):
    pass

class ProcessBase(cotyledon.Service):
    def __init__(self, worker_id, conf, interval_delay=0):
        super(ProcessBase, self).__init__(worker_id)
        self.conf = conf
        self.startup_delay = self.worker_id = worker_id
        self.interval_delay = interval_delay
        self._wake_up = threading.Event()
        self._shutdown = threading.Event()
        self._shutdown_done = threading.Event()
        # zk的listener是在另一个线程中，用于回调时的并发处理
        self._cond = threading.Condition()

    def lock(self):
        self._cond.acquire()

    def release(self):
        self._cond.release()

    # 用于ZK连接发生问题时回调使用
    def callback(self,state):
        with self._cond:
            self.zkcli.state_changes = True
            self.ha.leader = False
            self.state = state
            self.wakeup()

    def wakeup(self):
        self._cond.notify()

    def _configure(self):
        self.member_id = "%s.%s.%s" % (socket.gethostname(),
                          self.worker_id,
                          # NOTE(jd) Still use a uuid here so we're
                          # sure there's no conflict in case of
                          # crash/restart
                          str(uuid.uuid4()))
        self.drivers = utils.load_drivers('template_processor.drivers',
                                            self.conf.processor.providers.split(','),
                                            self.conf)
        self.zkcli = zk_common.ZKBase(self.conf,self)
        self.ha = zk_common.HAMaster(self.conf,self.zkcli,self)
        self.dbsession = sessionmaker(bind=create_engine(self.conf.processor.db_url))

    def run(self):
        self._configure()
        self.ha.elect()
        # Delay startup so workers are jittered.
        time.sleep(self.startup_delay)
        self._cond.acquire()
        while not self._shutdown.is_set():
            with utils.StopWatch() as timer:
                try:
                    if self.ha.leader:
                        self._run_job()
                    else:
                        LOG.info("Role is standby. Go to sleep， work id: %s." % self.worker_id)
                except Exception:
                    LOG.error("Unexpected error during %s job",
                              self.name,
                              exc_info=True)
            self._cond.wait(timeout=max(0, self.interval_delay - timer.elapsed()))
            if self.zkcli.state_changes:
                LOG.info("State changed. Reinit zk and ha...")
                self.zkcli.reinit(self.state)
                self.ha.reinit(self.state)
        self._cond.release()
        self._shutdown_done.set()

    def is_shutdown(self):
        return self._shutdown.is_set()

    def terminate(self):
        with self._cond:
            self._shutdown.set()
            self.wakeup()
        LOG.info("Waiting ongoing domain processing to finish")
        self._shutdown_done.wait()
        self.close_services()

    def close_services(self):
        self.zkcli.terminate()
        self.ha.terminate()

    @staticmethod
    def _run_job():
        raise NotImplementedError


class TemplateProcessor(ProcessBase):

    TEMPLATE_PATH = "/template/domains"

    def __init__(self,worker_id, conf):
        super(TemplateProcessor,self).__init__(worker_id,
                                            conf,
                                            conf.processor.domain_polling_interval)
        self.conf = conf
        self.pre = list()
        self.event_watch = threading.Event()

    def my_watch(self,event):
        if event.state == "CREATED":
            self.event_watch.set()
            self.wakeup()
        else:
            LOG.info("Not Concerned Event: %s" % event)
            

    def _run_job(self):
        if self.event_watch.is_set():
            while self.event_watch.is_set():
                self.event_watch.clear()
                cur = self.get_children(self.DOMAIN_PATH,watch=self.my_watch)
                domain_diff = set(cur).difference(set(self.pre))
                self.pre = cur
                for domain in domain_diff:
                    LOG.info("Polling domain status")
                    #TODO: Polling domain status
        else:
            #定期轮询状态
            LOG.info("Polling status")
            with self.dbsession() as session:
                domains = session.query(Domain).filter(TestModel.status != 'OK').all()
            #TODO
            #zdns_domains = 数据库
            #dnspod_domains = 数据库
            #describe每个domain的状态
            self.drivers['redis'].test()
            self.drivers['zk'].test()

class TemplateServiceManager(cotyledon.ServiceManager):
    def __init__(self, conf):
        super(TemplateServiceManager, self).__init__()
        oslo_config_glue.setup(self, conf)

        self.conf = conf
        self.processor_id = self.add(TemplateProcessor, args=(self.conf,),workers=conf.processor.workers)
        self.register_hooks(on_reload=self.on_reload)

    def on_reload(self):
        # NOTE(sileht): We do not implement reload() in Workers so all workers
        # will received SIGHUP and exit gracefully, then their will be
        # restarted with the new number of workers. This is important because
        # we use the number of worker to declare the capability in tooz and
        # to select the block of metrics to proceed.
        self.reconfigure(self.processor_id,
                         workers=self.conf.processor.workers)


def process():
    conf = cfg.ConfigOpts()
    conf = service.prepare_service(conf=conf)
    TemplateServiceManager(conf).run()