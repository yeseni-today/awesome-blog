import logging

logging.basicConfig(level=logging.INFO)
import asyncio
from aiohttp import web
import aiomysql
from www.orm import Model, StringField, IntegerField


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', content_type='html')


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return await handler(request)

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


async def init(loop):
    # aiohttp web application
    app = web.Application(loop=loop, middlewares=[
        logger_factory, response_factory
    ])
    # set route
    app.router.add_route('GET', "/", index)
    # async create server
    server = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://localhost:9000...')
    return server


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
