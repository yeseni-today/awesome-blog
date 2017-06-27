import time, uuid
from www.orm import Model, StringField, BooleanField, FloatField, TextField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'
    id = StringField(primary_key=True, default=next_id(), ddl='varchar(50)')
    email = StringField(ddl='varchar(50)', name='email')
    passwd = StringField(ddl='varchar(50)', name='passwd')
    admin = BooleanField(name='admin')
    name = StringField(ddl='varchar(50)', name='name')
    image = StringField(ddl='varchar(50)', name='image')
    create_at = FloatField(default=time.time(), name='create_at')


class Blog(Model):
    __table__ = 'blogs'
    id = StringField(primary_key=True, name='blogs', default=next_id(), ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    create_at = FloatField(default=time.time())
