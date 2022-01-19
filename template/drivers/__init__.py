# -*- coding: utf-8 -*-

import abc


class DriverBase(metaclass=abc.ABCMeta):
    """Base class for example plugin used in the tutorial.
    """

    def __init__(self, conf=None):
        self.conf = conf

    @abc.abstractmethod
    def test(self):
        """
        test
        """