import hashlib
import aiohttp
from aiohttp import web

from www.apis import APIValueError, APIError
from www.model import *
from www.web import *
import re, json
import www.utility as util


@get('/')
async def index(request):
    user = request.__user__
    if user is None:
        summary = 'Lorem ipsum dolor sit amet,' \
                  ' consectetur adipisicing elit,' \
                  ' sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
        blogs = [
            Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
            Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
            Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
        ]
    else:
        blogs = [
            Blog(id='1', name='Signin Success', summary="You signin success", created_at=time.time() - 120),
        ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/register')
async def register(request):
    return {
        '__template__': 'register.html'
    }


@get('/signin')
async def signin(request):
    return {
        '__template__': 'signin.html'
    }


@get('/api/users')
async def api_get_users():
    num = await User.findNumber('count(id)')
    if num == 0:
        return dict(users=())
    users = await User.findAll()
    for u in users:
        u.passwd = '******'
    return dict(users=users)


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name and not name.strip():
        raise APIValueError('name')
    if not email or not util.RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not util.RE_SHAL.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register failed', 'email', 'Email is already in use.')
    uid = next_id()
    shal_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email,
                passwd=hashlib.sha1(shal_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120'
                      % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    r = web.Response()
    r.set_cookie(util.COOKIE_NAME, util.user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if email is None:
        raise APIValueError('email', 'Invalid email.')
    if passwd is None:
        raise APIValueError('passwd', 'Invalid password.')
    user = await User.findAll('email=?', [email])
    if len(user) == 0:
        raise APIValueError('email', 'Email not exist')
    user = user[0]
    # check password
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password')
    # authorized ok, set cookie
    r = web.Response()
    r.set_cookie(util.COOKIE_NAME, util.user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

# @get('/api/users')
# async def api_get_users(*, page='1'):
#     page_index = get_page_index(page)
#     num = await User.findNumber('count(id)')
#     p = Page(num, page_index)
#     if num == 0:
#         return dict(page=p,users=())
#     users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
#     for u in users:
#         u.passwd = '******'
#     return dict(page=p,users=users)
