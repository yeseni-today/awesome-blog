import www.orm
from www.model import User, Blog


async def text(loop):
    await www.orm.create_pool(loop, user='root', password='', db='awesome')
    u = User(name='Test', email='test@example.com', passwd='123456789', image='about:blank')
    await u.save()

async def find(loop):
    await www.orm.create_pool(loop,user='root',password='',db='awesome')
    u = User.find('0014981898972745e30b0674f9b48a4bd3fe82e6ee006d0000')
    print(u)

import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(find(loop))
loop.run_forever()