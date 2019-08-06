import time, uuid
from orm import Model, IntegerField, StringField, BooleanField, FloatField, TextField

def next_id():
    return "%015d%s000" %(int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = "users"
    __schema__ = ['id','email','passwd','admin','name','image','created_at']
    '''
    The table for the users
    The schema should be consistent with the following sequence, and primary_key is alway the first
    '''

    id = StringField(primary_key=True,ddl="varchar(50)",default=next_id)
    email = StringField(ddl="varchar(50)")
    passwd = StringField(ddl="varchar(50)")
    admin = BooleanField()
    name = StringField(ddl="varchar(50)")
    image = StringField(ddl="varchar(500)")
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__= "blogs"
    __schema__=['id','user_id','user_name','user_image','title','category','digest','content','created_at']
    '''
    '''

    id = StringField(primary_key=True,ddl="varchar(50)",default=next_id)
    user_id = StringField(ddl="varchar(50)")
    user_name = StringField(ddl="varchar(50)")
    user_image = StringField(ddl="varchar(500)")
    title = StringField(ddl="varchar(500)")
    category = StringField(ddl="varchar(50)")
    digest = StringField(ddl="varchar(500)")
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):
    __table__= "comments"
    __schema__=['id','blog_id','user_id','user_name','user_image','content','created_at']
    '''
    '''

    id = StringField(primary_key=True,ddl="varchar(50)",default=next_id)
    blog_id = StringField(ddl="varchar(50)")
    user_id = StringField(ddl="varchar(50)")
    user_name = StringField(ddl="varchar(50)")
    user_image = StringField(ddl="varchar(500)")
    content = TextField()
    created_at = FloatField(default=time.time)



