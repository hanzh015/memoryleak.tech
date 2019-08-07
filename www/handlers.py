from coroweb import get, post
from models import User, Blog, Comment, next_id
from orm import select
from config import configs
import asyncio
from apis import get_page_index, Page, APIError, APIValueError, APIResourceNotFoundError, APIPermissionError
from aiohttp import web
from sqlite3 import Error
import json
import re
import hashlib
import time,math

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
GET /api/blogs                              Obtain blog list
GET /api/blogs/:blog_id                     Fetch the detailed blog
POST /api/blogs                             Create a blog
POST /api/blogs/:blog_id                    Update a blog
POST /api/blogs/:blog_id/delete             Delete a blog
GET /api/comments                           Obtain comments
POST /api/comments                          Create a comment
POST /api/comments/:comment_id/delete       Delete a comment
POST /api/users                             Create a new user
GET  /api/users                             Obtain users
POST /api/users/:user_id/delete             Delete the user (Only for admin)
POST /api/login                             User log in
POST /api/logout                            User log out

====================== Management Page ======================
GET  /manage/comments                       Comments list
GET  /manage/blogs                          Blogs list
GET  /manage/blogs/create                   Create a blog
GET  /manage/blogs/update/{blog_id}         Update a blog
GET  /manage/users                          Admin Stuff

======================= User Browsing =======================
GET  /                                      Index page
GET  /:category                             Index page filtered by category
GET  /blogs/:blog_id                        Detailed blog page

==================== Administrator Action ===================

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
async def get_blogs(*,page='1',size='8',order_by='created_at',desc=True,user=False,category=None,request):
    '''
    1. if user is set to False, then it is browser mode, enable selection by category
    2. otherwise, it is management mode, return blogs whose author is the current user.
    '''
    try:
        page,size = get_page_index(page,size)
    except APIError as e:
        raise APIValueError('Blog','GET /api/blogs '+e.data)
    
    if not user:
        if category:
            where='category=?'
            args=[category]
        else:
            where=None
            args=None
        num = await Blog.findNumber('count(id)',where,args)
        p = Page(num,page,size)
        des = ' desc' if desc is True else ' asc'
        blogs = await Blog.findAll(where,args,orderBy=order_by+des,limit=(p.offset,p.limit))
    else:
        if not request.__user__:
            raise APIPermissionError('blog','Log in to manage blogs')
        num = await Blog.findNumber('count(id)',where="user_id=?",args=[request.__user__.id])
        p = Page(num,page,size)
        des = ' desc' if desc is True else ' asc'
        blogs = await Blog.findAll('user_id=?',[request.__user__.id],orderBy=order_by+des,limit=(p.offset,p.limit))
    if len(blogs)==0:
        raise APIResourceNotFoundError('Blog','Could not found resource on your specified page')
    else:
        for blog in blogs:
            blog.content = ''
        return dict(total=p.page_count,page=page,blogs=blogs)

@get('/api/blogs/{blog_id}')
async def get_blog_details(*,blog_id):
    blog = await Blog.find(blog_id)
    if not blog:
        raise APIResourceNotFoundError(field="blog",message="blog not found")
    else:
        return blog

@post('/api/blogs')
async def create_blog(*,title,digest,content,category,request):
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
    kw = {'user_id':user.id,'user_name':user.name,'user_image':user.image,'title':title,'category':category,'digest':digest,'content':content}
    try:
        blog = Blog(**kw)
        await blog.save()
        return blog
    except Error as e:
        return dict(error='Datebase Error',message=str(e.args[0]))

@post('/api/blogs/{blog_id}')
async def update_blog(*,blog_id,title,digest,content,category,request):
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
            blog.category = category
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
        if not (blog.user_id==request.__user__.id or request.__user__.admin==1):
            raise APIPermissionError('User','Deleting is only accessible to the author or admins.')
        try:
            #delete comments as well
            comments = await Comment.findAll("blog_id=?",[blog.id])
            for c in comments:
                await c.remove()
            await blog.remove()
            return dict(message='succeed')
        except Error as e:
            return dict(error='Database Error',data="blogs",message=str(e.args[0]))
    else:
        raise APIResourceNotFoundError('Blog','Cannot found blog with id={}'.format(blog_id))

@get('/api/comments')
async def get_comments(*,page='1',size='8',blog_id=None,order_by="created_at",desc=True,user=False,request):
    '''
    To get the comments list. There are three exclusive modes
    1. If `user` is true, then return the inner joined comments list including blog title which is related to the the user.
    2. If `blog_id` is provided, then return the comments list under the blog
    3. If both are not provided, enable adminstrator mode which returns all current comments records. 
    '''
    try:
        page,size = get_page_index(page,size)
    except APIError as e:
        raise APIValueError('Comments','GET /api/comments '+e.data)
    des = ' desc' if desc is True else ' asc'
    if not blog_id:
        #use join select
        #Note: This piece of code is manually coded, need to be improved in the future
        if not request.__user__:
            raise APIPermissionError('comments','Log in to manage comments')
        if not (request.__user__.admin==1 or user):
            raise APIPermissionError('comments','Only administrators have access to all comments') 
        field_main = ['c.'+f for f in Comment.__schema__]
        field_min = ['b.title']
        query = "select {},{}".format(','.join(field_main),','.join(field_min))
        query += " from comments c inner join blogs b on c.blog_id=b.id"
        if user:
            query += " where c.user_id=?"
            args = [request.__user__.id]
            num = await Comment.findNumber('count(id)','user_id=?',[request.__user__.id])
        else:
            args = []
            num = await Comment.findNumber('count(id)')
        p = Page(num,page,size)
        query += " order by "+'c.'+order_by+des+" limit ?,?"
        args.extend([p.offset,p.limit])
        joined_comments = await select(query,args)
        schema = Comment.__schema__ + ['title']
        comments = list(map(lambda x:{k:v for k,v in zip(schema,x)},joined_comments))

    else:
        related_blog = await Blog.find(blog_id)
        if not related_blog:
            raise APIResourceNotFoundError('Comment','The related blog: {} is not found'.format(blog_id))
        where = 'blog_id=?'
        args = [blog_id]
        num = await Comment.findNumber('count(id)',where,args)
        p = Page(num,page,size)
        comments = await Comment.findAll(where,args,orderBy=order_by+des,limit=(p.offset,p.limit))

    if len(comments)==0:
        raise APIResourceNotFoundError('Comment','Could not found resource on your specified page')
    else:
        return dict(total=p.page_count,page=page,comments=comments)

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
        return dict(error='Datebase Error',data='comments',message=str(e.args[0]))

@post('/api/comments/{comment_id}/delete')
async def delete_comment(*,comment_id,request):
    if not request.__user__:
        raise APIPermissionError('Comment','Please login first')
    comment = await Comment.find(comment_id)
    if comment:
        blog = await Blog.find(comment.blog_id)
        if not (request.__user__.id==comment.user_id or request.__user__.id==blog.user_id or request.__user__.admin==1):
            raise APIPermissionError('Comment','Deleting is only accessible to blog author, comment maker or admins')
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
async def create_user(*,email,passwd,name,invitation):
    #user registry api
    if not name or not name.strip():
        raise APIValueError('name','name has to contain at least one non space letter')
    if not _RE_EMAIL.match(email):
        raise APIValueError('email','invalid email')
    if not _RE_SHA1.match(passwd):
        raise APIValueError('passwd','unencrypted password')
    if not configs.invitation == hashlib.sha1(invitation.encode('utf-8')).hexdigest():
        raise APIPermissionError('invitation code','wrong invitation code')
    
    users = await User.findAll(where="email=?",args=[email,])
    if len(users)!=0:
        raise APIValueError('email','this email already exists')
    uid = next_id()
    concatenate_passwd = "{}:{}".format(uid,passwd)
    user = User(email=email,id=uid,passwd=hashlib.sha1(concatenate_passwd.encode('utf-8')).hexdigest(),
name=name,image='http://www.gravatar.com/avatar/{}?d=robohash&s=120'.format(hashlib.md5(email.encode('utf-8')).hexdigest()))
    await user.save()
    res = web.Response(status=200)
    res.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd='********'
    res.content_type = 'application/json'
    res.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return res
    

@get('/api/users')
async def get_users(*,page='1',size='8',order_by='created_at',desc=True,request):
    try:
        page,size = get_page_index(page,size)
    except APIError as e:
        raise APIValueError('User','GET /api/users '+e.data)
    if not request.__user__:
        raise APIPermissionError("User","Log in to manage users")
    if request.__user__.admin == 0:
        raise APIPermissionError("User",'Only administrators have access to the user list')
    
    num = await User.findNumber('count(id)')
    p = Page(num,page,size)
    des = ' desc' if desc is True else ' asc'
    users = await User.findAll(orderBy=order_by+des,limit=(p.offset,p.limit))
    if len(users)==0:
        raise APIResourceNotFoundError('User','Could not found resource on your specified page')
    else:
        for user in users:
            user.passwd = '********'
        return dict(total=p.page_count,page=page,users=users)

@post('/api/users/{user_id}/delete')
async def delete_user(*,user_id,request):
    if not request.__user__:
        raise APIPermissionError('User','Log in to manage users')
    if not request.__user__.admin==1:
        raise APIPermissionError('User','Only admins have access to manage accounts')
    try:
        user = await User.find(user_id)
        if not user:
            raise APIResourceNotFoundError('User','User record doesnt exist')
        await user.remove()
        return dict(message='Succeed')
    except Error as e:
        return dict(error='Database Error',data="blogs",message=str(e.args[0]))

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
    
@post('/api/logout')
async def log_out():
    res = web.Response()
    res.set_cookie(COOKIE_NAME,";",max_age=0,httponly=True)
    res.content_type = 'application/json'
    res.body = json.dumps({'status':'logged out'},ensure_ascii=False).encode('utf-8')
    return res

@post('/api/test_login')
async def test_login(*,request):
    if request.__user__:
        return web.Response(status=201,body=json.dumps(request.__user__,ensure_ascii=False).encode('utf-8'))
    else:
        return 404

@get('/')
async def get_index(*,request):
    if request.__user__:
        request.__user__['status'] = 'Succeed'
        user_state = json.dumps(request.__user__,ensure_ascii=False)
    else:
        user_state = json.dumps({'status':'logged out'},ensure_ascii=False)
    return {
        '__template__': 'blogs.html',
        'user':user_state,
        'category':'index',
    }

@get('/{category}')
async def get_category_blogs(*,category,request):
    if request.__user__:
        request.__user__['status'] = 'Succeed'
        user_state = json.dumps(request.__user__,ensure_ascii=False)
    else:
        user_state = json.dumps({'status':'logged out'},ensure_ascii=False)
    return {
        '__template__': 'blogs.html',
        'user':user_state,
        'category':category
    }

@get('/blogs/{blog_id}')
async def get_blog_page(*,blog_id,request):
    blog = await Blog.find(blog_id)
    if not blog:
        return 404
    else:
        if request.__user__:
            request.__user__['status'] = 'Succeed'
            user_state = json.dumps(request.__user__,ensure_ascii=False)
        else:
            user_state = json.dumps({'status':'logged out'},ensure_ascii=False)
        return {
            '__template__': 'blog_details.html',
            'blog' : blog,
            'user' : user_state,
            'title': blog.title
        }

@get('/manage/blogs/create')
async def get_manage_create(*,request):
    if request.__user__:
        request.__user__['status'] = 'Succeed'
        user_state = json.dumps(request.__user__,ensure_ascii=False)
    else:
        user_state = json.dumps({'status':'logged out'},ensure_ascii=False)
    return {
        '__template__': 'manage_create_posts.html',
        'init':'',
        'user': user_state,
        'title':"create a new post"
    }

@get('/manage/blogs/update/{blog_id}')
async def get_manage_update(*,blog_id,request):
    blog = await Blog.find(blog_id)
    if not blog:
        return 404
    else:
        if request.__user__:
            if request.__user__.id == blog.user_id:
                request.__user__['status'] = 'Succeed'
                user_state = json.dumps(request.__user__,ensure_ascii=False)
                return {
                    '__template__':'manage_create_posts.html',
                    'init':blog_id,
                    'user':user_state,
                    'title':"update --- "+blog.title
                }
            else:
                return 403
        else:
            return 401

@get('/manage/blogs')
async def manage_blogs(*,request):
    if not request.__user__:
        return 401
    else:
        request.__user__['status'] = 'Succeed'
        user_state = json.dumps(request.__user__,ensure_ascii=False)
        return {
            '__template__':'manage_list.html',
            'category':'blog',
            'user':user_state,
            'title':"manage my posts"
        }

@get('/manage/comments')
async def manage_comments(*,request):
    if not request.__user__:
        return 401
    else:
        request.__user__['status'] = 'Succeed'
        user_state = json.dumps(request.__user__,ensure_ascii=False)
        return {
            '__template__':'manage_list.html',
            'category':'comment',
            'user':user_state,
            'title':"manage my comments"
        }

@get('/manage/users')
async def manage_users(*,request):
    if not request.__user__:
        return 401
    elif not request.__user__.admin==1:
        return 403
    else:
        request.__user__['status'] = 'Succeed'
        user_state = json.dumps(request.__user__,ensure_ascii=False)
        return {
            '__template__':'manage_all.html',
            'user':user_state
        }
