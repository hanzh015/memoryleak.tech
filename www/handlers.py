from coroweb import get, post
from models import User, Blog, Comment
import asyncio
from apis import get_page_index, Page, APIError, APIValueError, APIResourceNotFoundError
from aiohttp import web
from sqlite3 import Error
import json

COOKIE_NAME = 'authentication'
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
    return None



@get('/api/blogs')
async def get_blogs(*,page='1',order_by='created_at',desc=True):
    try:
        page = get_page_index(page)
    except APIError as e:
        raise APIValueError('GET /apis/blogs '+e.data)
    
    num = await Blog.findNumber('count(id)')
    p = Page(num,page)
    des = ' desc' if desc is True else ' asc'
    blogs = Blog.findAll(orderBy='order by '+order_by+des,limit=(p.offset,p.limit))
    if len(blogs)==0:
        raise APIResourceNotFoundError('Blog','Could not found resource on your specified page')
    else:
        for blog in blogs:
            blog.content = ''
        return dict(page=page,blogs=blogs)

@post('/api/blogs')
async def create_blog(**kw):
    for field in Blog.__fields__:
        if not field in kw:
            raise APIValueError('Blog','{} not found in Blog\'s field'.format(field))
    if Blog.__primary_key__ not in kw:
        raise APIValueError('Blog','primary key not found')
    for k in kw.keys():
        if not (k in Blog.__fields__ or k==Blog.__primary_key__):
            raise APIValueError('Blog','Additional resource provided: {}'.format(k))
    try:
        blog = Blog(**kw)
        await blog.save()
        return 201
    except Error as e:
        return dict(error='Datebase Error',message=str(e.args[0]))

@post('/api/blogs/{blog_id}')
async def update_blog(**kw):
    for field in Blog.__fields__:
        if not field in kw:
            raise APIValueError('Blog','{} not found in Blog\'s field'.format(field))
    blog_id = kw.pop('blog_id')
    kw['id']=blog_id
    f = await Blog.find(kw['id'])
    if f:
        for k in kw.keys():
            if not (k in Blog.__fields__ or k==Blog.__primary_key__):
                raise APIValueError('Blog','Additional resource provided: {}'.format(k))
        try:
            blog = Blog(**kw)
            await blog.update()
            return 201
        except Error as e:
            return dict(error='Datebase Error', message=str(e.args[0]))
    else:
        raise APIResourceNotFoundError('BLog','Cannot found blog with id={}'.format(kw['id']))