import unittest
import time
from datetime import datetime
import requests
from database_test import next_email
import hashlib
'''
ATTENTION: IN test_create_blog case, you should first give a existing account
'''


_EMAIL = next_email() + "@dummy.com"
_PASSWORD = hashlib.sha1((next_email() + "api_test").encode('utf-8')).hexdigest()
_NAME = 'jiangzemin'
_URL = 'http://127.0.0.1:9000'
_COOKIE_NAME = 'authentication'
_UID = ''
_BID = ''
_CID = ''
class TestAPI(unittest.TestCase):

    def test_register_user(self):
        '''
        POST /api/users
            check response cookie
        GET  /api/users
            check if the user exist
        '''
        usr = {'email':_EMAIL,'passwd':_PASSWORD,'name':_NAME}
        print('email: '+_EMAIL)
        print('password: '+_PASSWORD)
        r = requests.post(_URL + '/api/users', data=usr)
        self.assertEqual(r.status_code,201)
        self.assertIsNotNone(r.cookies[_COOKIE_NAME])
        u_id = r.json()['id']
        global _UID
        _UID = u_id

        re = requests.get(_URL + '/api/users',data={'page':1,'order_by':'created_at'})
        res = re.json()
        users = res['users']
        u_ids = [u['id'] for u in users]
        self.assertIn(u_id,u_ids)

    def test_user_login(self):
        '''
        POST /api/login
            check response cookie
        POST /api/test_login
            check if login
        '''
        global _UID
        logins = {'email':_EMAIL,'password':_PASSWORD}
        r = requests.post(_URL+'/api/login',data=logins)
        self.assertEqual(_UID,r.json()['id'])
        cookie_str = r.cookies[_COOKIE_NAME]

        ck = {_COOKIE_NAME:cookie_str}
        #test login
        l = requests.post(_URL + '/api/test_login',cookies=ck,data={'a':'b'})
        self.assertEqual(l.status_code,201)

        logins1 = {'email':_EMAIL,'password':_PASSWORD+'1'}
        r = requests.post(_URL+'/api/login',data=logins1)
        self.assertEqual(r.json()['error'],'value:invalid')


    def test_create_blog(self):
        '''
        POST /api/blogs
        GET  /api/blogs
            check if the blog exist
        POST /api/blogs/{blog_id}
        GET  /api/blogs
            check update blog
        POST /api/blogs/{blog_id}/delete
        GET  /api/blogs
            check if deleted
        '''
        #login first
        #The following account is already exist in the database
        email = '4daa03@dummy.com'
        password = '66b7c2391d28c6ddfc5626851375c9ab60f5903f'
        logins = {'email':email,'password':password}
        r = requests.post(_URL+'/api/login',data=logins)
        cookie_str = r.cookies[_COOKIE_NAME]
        ck = {_COOKIE_NAME:cookie_str}

        #create a blog
        blog = {'title':'genesis','digest':'test post','content':'Testing this system.'}
        b = requests.post(_URL + '/api/blogs',data=blog,cookies=ck)
        self.assertIsNotNone(b.json()['id'])
        global _BID
        _BID = b.json()['id']

        c = requests.get(_URL + '/api/blogs',data={'page':1,'order_by':'created_at'})
        c = c.json()['blogs']
        ids = [blog['id'] for blog in c]
        self.assertIn(_BID,ids)

        #update a blog
        blog['content']='Testing again'
        b = requests.post(_URL + '/api/blogs/'+_BID,data=blog,cookies=ck)
        self.assertEqual(b.json()['content'],'Testing again')
        
        #delete a blog
        b = requests.post(_URL + '/api/blogs/'+_BID+'/delete',data={'a':'b'},cookies=ck)
        try:
            reply = b.json()
        except:
            print(b.text)
        self.assertEqual(reply['message'],'succeed')
        c = requests.get(_URL + '/api/blogs',data={'page':1,'order_by':'created_at'})
        c = c.json()['blogs']
        ids = [blog['id'] for blog in c]
        self.assertNotIn(_BID,ids)

    def test_create_comment(self):
        '''
        POST /api/comments
        GET  /api/comments
            check if the comment exist
        POST /api/comments/{comment_id}/delete
        GET  /api/comments
            check if deleted
        '''
        email = '2adfee@dummy.com'
        password = 'c995084a5fe8300f4726d7f0714a6726f18bbc58'
        #login first
        logins = {'email':email,'password':password}
        r = requests.post(_URL+'/api/login',data=logins)
        cookie_str = r.cookies[_COOKIE_NAME]
        ck = {_COOKIE_NAME:cookie_str}

        #create a comment
        blog_id = '001561950111158dedd6baf0605430bac2b63f95be52b0b000'
        comment = {'blog_id':blog_id,'content':'awesome post!'}
        r = requests.post(_URL+'/api/comments',data=comment,cookies=ck)
        global _CID
        _CID = r.json()['id']
        c = requests.get(_URL+'/api/comments',data={'page':1,'order_by':'created_at'})
        c = c.json()['comments']
        ids = [comment['id'] for comment in c]
        self.assertIn(_CID,ids)

        #delete by author
        r = requests.post(_URL+'/api/comments/'+_CID+'/delete',data={'a':'b'},cookies=ck)
        #print(r.text)
        self.assertEqual(r.json()['message'],'succeed')
        c = requests.get(_URL+'/api/comments',data={'page':1,'order_by':'created_at'})
        c = c.json()['comments']
        ids = [comment['id'] for comment in c]
        self.assertNotIn(_CID,ids)

        #recreate
        blog_id = '001561950111158dedd6baf0605430bac2b63f95be52b0b000'
        comment = {'blog_id':blog_id,'content':'awesome post!'}
        r = requests.post(_URL+'/api/comments',data=comment,cookies=ck)
        _CID = r.json()['id']
        #login as blog owner
        email = '4daa03@dummy.com'
        password = '66b7c2391d28c6ddfc5626851375c9ab60f5903f'
        logins = {'email':email,'password':password}
        r = requests.post(_URL+'/api/login',data=logins)
        cookie_str = r.cookies[_COOKIE_NAME]
        ck = {_COOKIE_NAME:cookie_str}
        #delete by blog owner
        r = requests.post(_URL+'/api/comments/'+_CID+'/delete',data={'a':'b'},cookies=ck)
        self.assertEqual(r.json()['message'],'succeed')
        c = requests.get(_URL+'/api/comments',data={'page':1,'order_by':'created_at'})
        c = c.json()['comments']
        ids = [comment['id'] for comment in c]
        self.assertNotIn(_CID,ids)


if __name__=='__main__':
    unittest.main()