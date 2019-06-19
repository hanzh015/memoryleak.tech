import time, uuid
from orm import Model, IntegerField, StringField, BooleanField, FloatField, TextField

def next_id():
    return "%015d%s000" %(int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = "users"
    '''
    The table for the users
    '''

    id = StringField(primary_key=True,ddl="varchar(50)",default=next_id)
    admin = BooleanField()
    email = StringField(ddl="varchar(50)")
    passwd = StringField(ddl="varchar(50)")
    name = StringField(ddl="varchar(50)")
    image = StringField(ddl="varchar(500)")
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__= "blogs"
    '''
    '''

    id = StringField(primary_key=True,ddl="varchar(50)",default=next_id)
    user_id = StringField(ddl="varchar(50)")
    user_name = StringField(ddl="varchar(50)")
    user_image = StringField(ddl="varchar(500)")
    title = StringField(ddl="varchar(500)")
    digest = StringField(ddl="varchar(500)")
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):
    __table__= "comments"
    '''
    '''

    id = StringField(primary_key=True,ddl="varchar(50)",default=next_id)
    blog_id = StringField(ddl="varchar(50)")
    user_id = StringField(ddl="varchar(50)")
    user_name = StringField(ddl="varchar(50)")
    user_image = StringField(ddl="varchar(500)")
    content = TextField()
    created_at = FloatField(default=time.time)



