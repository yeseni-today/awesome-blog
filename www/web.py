import functools
import inspect
import logging


def get(path):
    """
    The decorator of url router of GET method
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator


def post(path):
    """
    The decorator of url router of GET method
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper

    return decorator


class RequestHandler(object):
    def __init__(self, app, func: function):
        self._app = app
        self._func = func

    async def __call__(self, request):
        # todo
        # self._func.
        r = await self._func()
        return r


def add_route(app, func):
    method = getattr(func, '__method__', None)
    path = getattr(func, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s' % str(func))
    logging.info('add route %s %s => %s(%s)' % (
        method, path, func.__name__, ', '.join(inspect.signature(func).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, func))


def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n + 1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        func = getattr(mod, attr)
        if callable(func):
            method = getattr(func, '__method__', None)
            path = getattr(func, '__route__', None)
            if method and path:
                add_route(app, func)
