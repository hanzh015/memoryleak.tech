from coroweb import get, post
from models import User, Blog, Comment, next_id
import asyncio
from apis import get_page_index, Page, APIError, APIValueError, APIResourceNotFoundError, APIPermissionError
from aiohttp import web
from sqlite3 import Error
import json
import re
import hashlib
import time

COOKIE_NAME = 'authentication'
COOKIE_KEY = 'toad'
'''
@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__':'test.html',
        'users':users
    }
'''

'''
THE DESIGN FOR RESTful API
======================= Backend AJAX =======================
GET /api/blogs                              Obtain blog
POST /api/blogs                             Create a blog
POST /api/blogs/:blog_id                    Update a blog
POST /api/blogs/:blog_id/delete             Delete a blog
GET /api/comments                           Obtain comments
POST /api/comments                          Create a comment
POST /api/comments/:comment_id/delete       Delete a comment
POST /api/users                             Create a new user
GET  /api/users                             Obtain users
POST /api/login                             User log in

====================== Management Page ======================
GET  /manage/comments                       Comments list
GET  /manage/blogs                          Blogs list
GET  /manage/blogs/create                   Create a blog
GET  /manage/blogs/update                   Update a blog
GET  /manage/users                          Users list

======================= User Browsing =======================
GET  /register                              User registry
GET  /signin                                User sign in
GET  /signout                               User sign out
GET  /                                      Index page
GET  /blogs/:blog_id                        Detailed blog page
'''

async def cookie2user(cookie_str):
    fields = cookie_str.split('-')
    if len(fields)==3:
        #check if expired
        if int(time.time())<=int(fields[1]):
            user = await User.find(fields[0])
            if user:
                check_hash = "{}-{}-{}-{}".format(user.id,user.passwd,fields[1],COOKIE_KEY)
                check_hash = hashlib.sha1(check_hash.encode('utf-8')).hexdigest()
                if check_hash==fields[2]:
                    user.passwd="********"
                    return user
    return None

def user2cookie(user,max_age):
    expire = int(time.time()+max_age)
    secret = "{}-{}-{}-{}".format(user.id,user.passwd,expire,COOKIE_KEY)
    L = [str(user.id),str(expire),hashlib.sha1(secret.encode('utf-8')).hexdigest()]
    return '-'.join(L)



def kw_check(model,kwargs):
    miss, addition = [],[]
    for field in model.__fields__:
        if not field in kwargs:
            miss.append(field)
    for k in kwargs:
        if not (k in model.__fields__ or k==model.__primary_key__):
            addition.append(k)
    if not model.__primary_key__ in kwargs:
        miss.append(model.__primary_key__)
    return miss,addition


@get('/api/blogs')
async def get_blogs(*,page='1',order_by='created_at',desc=True):
    try:
        page = get_page_index(page)
    except APIError as e:
        raise APIValueError('Blog','GET /api/blogs '+e.data)
    
    num = await Blog.findNumber('count(id)')
    p = Page(num,page)
    des = ' desc' if desc is True else ' asc'
    blogs = await Blog.findAll(orderBy=order_by+des,limit=(p.offset,p.limit))
    if len(blogs)==0:
        raise APIResourceNotFoundError('Blog','Could not found resource on your specified page')
    else:
        for blog in blogs:
            blog.content = ''
        return dict(page=page,blogs=blogs)

@post('/api/blogs')
async def create_blog(*,title,digest,content,request):
    '''
    miss, addi = kw_check(Blog,kw)
    if addi:
        raise APIValueError('Blog','Additional resource provided: {}'.format(addi[0]))
    if miss:
        for key in miss:
            if not (key==Blog.__primary_key__ or key=="created_at"):
                raise APIValueError('Blog','compulsory key: {} not found'.format(key))
    '''
    if not request.__user__:
        raise APIPermissionError('User','Please login first')
    user = request.__user__
    kw = {'user_id':user.id,'user_name':user.name,'user_image':user.image,'title':title,'digest':digest,'content':content}
    try:
        blog = Blog(**kw)
        await blog.save()
        return blog
    except Error as e:
        return dict(error='Datebase Error',message=str(e.args[0]))

@post('/api/blogs/{blog_id}')
async def update_blog(*,blog_id,title,digest,content,request):
    if not request.__user__:
        raise APIPermissionError('User','Please login first')
    blog = await Blog.find(blog_id)
    if blog:
        if not blog.user_id==request.__user__.id:
            raise APIPermissionError('User','Update only accessible to the author')
        try:
            blog.title = title
            blog.digest = digest
            blog.content = content
            await blog.update()
            return blog
        except Error as e:
            return dict(error='Datebase Error', message=str(e.args[0]))
    else:
        raise APIResourceNotFoundError('BLog','Cannot found blog with id={}'.format(blog_id))

@post('/api/blogs/{blog_id}/delete')
async def delete_blog(*,blog_id,request):
    if not request.__user__:
        raise APIPermissionError('User','Please login first')
    blog = await Blog.find(blog_id)
    if blog:
        if not blog.user_id==request.__user__.id:
            raise APIPermissionError('User','Delete only accessible to the author')
        try:
            await blog.remove()
            return dict(message='succeed')
        except Error as e:
            return dict(error='Database Error',message=str(e.args[0]))
    else:
        raise APIResourceNotFoundError('Blog','Cannot found blog with id={}'.format(blog_id))

@get('/api/comments')
async def get_comments(*,page=1,blog_id=None,order_by="created_at",desc=True):
    try:
        page = get_page_index(page)
    except APIError as e:
        raise APIValueError('Comments','GET /api/comments '+e.data)
    if blog_id:
        related_blog = await Blog.find(blog_id)
        if not related_blog:
            raise APIResourceNotFoundError('Comment','The related blog: {} is not found'.format(blog_id))
        where = 'blog_id={}'.format(blog_id)
    else:
        where = None

    num = await Comment.findNumber('count(id)',where)
    p = Page(num,page)
    des = ' desc' if desc is True else ' asc'
    comments = await Comment.findAll(where,orderBy=order_by+des,limit=(p.offset,p.limit))
    if len(comments)==0:
        raise APIResourceNotFoundError('Comment','Could not found resource on your specified page')
    else:
        return dict(page=page,comments=comments)

@post('/api/comments')
async def create_comment(*,blog_id,content,request):
    if not request.__user__:
        raise APIPermissionError('Comment','Please login first')
    user = request.__user__
    kw = {'blog_id':blog_id,'user_id':user.id,'user_name':user.name,'user_image':user.image,'content':content}
    try:
        comment = Comment(**kw)
        await comment.save()
        return comment
    except Error as e:
        return dict(error='Datebase Error',message=str(e.args[0]))

@post('/api/comments/{comment_id}/delete')
async def delete_comment(*,comment_id,request):
    if not request.__user__:
        raise APIPermissionError('Comment','Please login first')
    comment = await Comment.find(comment_id)
    if comment:
        blog = await Blog.find(comment.blog_id)
        if not (request.__user__.id==comment.user_id or request.__user__.id==blog.user_id):
            raise APIPermissionError('Comment','Delete only accessible to blog author or comment maker')
        try:
            await comment.remove()
            return dict(message="succeed")
        except Error as e:
            return dict(error='Database Error',message=str(e.args[0]))
    else:
        raise APIResourceNotFoundError('Comment','Cannot found comment with id={}'.format(comment_id))


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-z]{40}$')
@post('/api/users')
async def create_user(*,email,passwd,name):
    #user registry api
    if not name or not name.strip():
        raise APIValueError('name','name has to contain at least one non space letter')
    if not _RE_EMAIL.match(email):
        raise APIValueError('email','invalid email')
    if not _RE_SHA1.match(passwd):
        raise APIValueError('passwd','unencrypted password')
    
    users = await User.find(email)
    if users:
        raise APIValueError('email','this email already exists')
    uid = next_id()
    concatenate_passwd = "{}:{}".format(uid,passwd)
    user = User(email=email,id=uid,passwd=hashlib.sha1(concatenate_passwd.encode('utf-8')).hexdigest(),
name=name,image='http://www.gravatar.com/avatar/{}?d=robohash&s=120'.format(hashlib.md5(email.encode('utf-8')).hexdigest()))
    await user.save()
    res = web.Response(status=201)
    res.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd='********'
    res.content_type = 'application/json'
    res.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return res
    

@get('/api/users')
async def get_users(*,page=1,order_by='created_at',desc=True):
    try:
        page = get_page_index(page)
    except APIError as e:
        raise APIValueError('User','GET /api/users '+e.data)
    
    num = await User.findNumber('count(id)')
    p = Page(num,page)
    des = ' desc' if desc is True else ' asc'
    users = await User.findAll(orderBy=order_by+des,limit=(p.offset,p.limit))
    if len(users)==0:
        raise APIResourceNotFoundError('User','Could not found resource on your specified page')
    else:
        for user in users:
            user.passwd = '********'
        return dict(page=page,users=users)

@post('/api/login')
async def authenticate(*,email,password):
    if not email:
        raise APIValueError('email')
    if not password:
        raise APIValueError('password')
    
    user = await User.findAll('email=?',[email])
    if len(user)==0:
        raise APIResourceNotFoundError('User','this email is not registered')
    user = user[0]
    encryp_passwd = hashlib.sha1()
    encryp_passwd.update(user.id.encode('utf-8'))
    encryp_passwd.update(b':')
    encryp_passwd.update(password.encode('utf-8'))
    if encryp_passwd.hexdigest()!=user.passwd:
        raise APIValueError('password','wrong password')
    #set cookie
    res = web.Response()
    res.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd="********"
    res.content_type = 'application/json'
    res.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return res
    
@post('/api/test_login')
async def test_login(*,request):
    if request.__user__:
        return web.Response(status=201,body=json.dumps(request.__user__,ensure_ascii=False).encode('utf-8'))
    else:
        return 404
