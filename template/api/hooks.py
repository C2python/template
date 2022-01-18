# -*- coding: utf-8 -*-

from pecan import hooks

class ConfigHook(hooks.PecanHook):
    """Attach the configuration and policy enforcer object to the request.

    That allows controllers to get it.
    """

    def __init__(self, conf):
        self.conf = conf

    def before(self, state):
        state.request.cfg = self.conf


class TranslationHook(hooks.PecanHook):

    def after(self, state):
        # After a request has been done, we need to see if
        # ClientSideError has added an error onto the response.
        # If it has we need to get it info the thread-safe WSGI
        # environ to be used by the ParsableErrorMiddleware.
        if hasattr(state.response, 'translatable_error'):
            state.request.environ['translatable_error'] = (
                state.response.translatable_error)