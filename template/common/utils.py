# -*- coding: utf-8 -*-

import string
import uuid
import monotonic
from oslo_log import log
from stevedore import named
import sys

from template.exceptions import tmp_except

LOG = log.getLogger(__name__)

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

def _catch_extension_load_error(mgr, ep, exc):
    # Extension raising ExtensionLoadError can be ignored,
    # and ignore anything we can't import as a safety measure.
    if isinstance(exc, tmp_except.ExtensionLoadError):
        LOG.error("loading extension error for %s: %s. Exit",
                  ep.name, exc.msg)
        raise exc
    LOG.error("Failed to import extension for %(name)r: "
              "%(error)s",
              {'name': ep.name, 'error': exc})
    raise exc

def _catch_extension_missing_error(names):
    LOG.error("Couldnot find provider drivers： %s" % names)
    raise tmp_except.ExtensionLoadError('Import Error')

def load_drivers(namespace,names,conf):
    """
    return:
        {
            'zk',zkcli
            'redis': rediscli
        }
    """
    LOG.info("Start load drivers: %s, namespace: %s" % (names,namespace))
    drivers = dict()
    extensions = named.NamedExtensionManager(
        namespace = namespace,
        names = names,
        invoke_on_load = True,
        invoke_args = (conf,),
        on_load_failure_callback =  _catch_extension_load_error,
        on_missing_entrypoints_callback = _catch_extension_missing_error,
    )
    for drv in extensions:
        drivers[drv.name] = drv.obj
    
    LOG.info("Load providers: %s" % str(drivers))

    return drivers
    
class StopWatch(object):
    """A simple timer/stopwatch helper class.

    Inspired by: apache-commons-lang java stopwatch.

    Not thread-safe (when a single watch is mutated by multiple threads at
    the same time). Thread-safe when used by a single thread (not shared) or
    when operations are performed in a thread-safe manner on these objects by
    wrapping those operations with locks.

    It will use the `monotonic`_ pypi library to find an appropriate
    monotonically increasing time providing function (which typically varies
    depending on operating system and python version).

    .. _monotonic: https://pypi.python.org/pypi/monotonic/
    """
    _STARTED = object()
    _STOPPED = object()

    def __init__(self):
        self._started_at = None
        self._stopped_at = None
        self._state = None

    def start(self):
        """Starts the watch (if not already started).

        NOTE(harlowja): resets any splits previously captured (if any).
        """
        if self._state == self._STARTED:
            return self
        self._started_at = monotonic.monotonic()
        self._state = self._STARTED
        return self

    @staticmethod
    def _delta_seconds(earlier, later):
        # Uses max to avoid the delta/time going backwards (and thus negative).
        return max(0.0, later - earlier)

    def elapsed(self):
        """Returns how many seconds have elapsed."""
        if self._state not in (self._STARTED, self._STOPPED):
            raise RuntimeError("Can not get the elapsed time of a stopwatch"
                               " if it has not been started/stopped")
        if self._state == self._STOPPED:
            elapsed = self._delta_seconds(self._started_at, self._stopped_at)
        else:
            elapsed = self._delta_seconds(
                self._started_at, monotonic.monotonic())
        return elapsed

    def __enter__(self):
        """Starts the watch."""
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        """Stops the watch (ignoring errors if stop fails)."""
        try:
            self.stop()
        except RuntimeError:
            pass

    def stop(self):
        """Stops the watch."""
        if self._state == self._STOPPED:
            return self
        if self._state != self._STARTED:
            raise RuntimeError("Can not stop a stopwatch that has not been"
                               " started")
        self._stopped_at = monotonic.monotonic()
        self._state = self._STOPPED
        return self

    def reset(self):
        """Stop and re-start the watch."""
        self.stop()
        return self.start()