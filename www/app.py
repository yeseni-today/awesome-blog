import logging

from jinja2 import Environment, FileSystemLoader

from www.model import *
from aiohttp import web
from www.web import *
from www.utility import *
import os, time, json, asyncio
from datetime import datetime
import www.orm as orm
import www.utility as util

logging.basicConfig(level=logging.INFO)


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return (await handler(request))

    return logger


async def response_factory(app, handler):
    async def response(request):
        ori_res = await handler(request)
        if isinstance(ori_res, web.StreamResponse):
            return ori_res
        if isinstance(ori_res, bytes):
            resp = web.Response(body=ori_res)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(ori_res, str):
            resp = web.Response(body=ori_res.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(ori_res, dict):
            template = ori_res.get('__template__')
            if template is None:
                resp = web.Response(
                    body=json.dumps(ori_res, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                ori_res['user'] = request.__user__
                resp = web.Response(body=app['__templating__'].get_template(template).render(**ori_res).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'

                return resp

    return response


async def authenticate_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str is not None:
            user = await util.cookie2user(cookie_str)
            if user is not None:
                logging.info('set current user: %s' % user.email)
                request.__user__ = user
        return (await handler(request))

    return auth


def datetime_filter(t):
    detail = int(time.time() - t)
    if detail < 60:
        return u'1分钟前'
    if detail < 3600:
        return u'%s分钟前' % (detail // 60)
    if detail < 86400:
        return u'%s小时前' % (detail // 3600)
    if detail < 604800:
        return u'%s天前' % (detail // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def init(loop):
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='', db='awesome')
    # aiohttp web application
    app = web.Application(loop=loop, middlewares=[
        logger_factory, response_factory, authenticate_factory
    ])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    # set route
    # app.router.add_route('GET', "/", index)
    add_routes(app, 'handlers')
    add_static(app)
    # async create server
    server = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://localhost:9000...')
    return server


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
