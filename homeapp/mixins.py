# -*- coding: utf-8 -*-


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def dispatch(self, request, *args, **kwargs):
        method = request.method.lower()
        if request.is_ajax():
            method += '_ajax'
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, method, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
