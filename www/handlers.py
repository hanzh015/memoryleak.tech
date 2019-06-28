from coroweb import get, post
from models import User, Blog, Comment
import asyncio
from apis import get_page_index, Page, APIError, APIValueError, APIResourceNotFoundError
from aiohttp import web

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


