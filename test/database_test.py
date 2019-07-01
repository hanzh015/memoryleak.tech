import unittest
import importlib
import asyncio
import time,os
from contextlib import contextmanager
import hashlib
from datetime import datetime

@contextmanager
def add_to_path(p):
    import sys
    old_path = sys.path
    sys.path = sys.path[:]
    sys.path.insert(0, p)
    try:
        yield
    finally:
        sys.path = old_path

def path_import(name,absolute_path):
   '''implementation taken from https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly'''
   with add_to_path(os.path.dirname(absolute_path)):
       spec = importlib.util.spec_from_file_location(name, absolute_path)
       module = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(module)
       return module

orm = path_import('orm','../www/orm.py')
models = path_import('models','../www/models.py')

def next_email():
    t = str(time.time())
    a = hashlib.sha256(t.encode('ascii'))
    return a.hexdigest()[-6:]
#orm.setDatabase('../www/awesome.db')

class TestOrm(unittest.TestCase):
    #tester for basic sql executions
    def test_insert_select(self):
        loop = asyncio.get_event_loop()
        #insert one entry for every table
        idd = models.next_id()
        insert_user = "insert into users (email, passwd, admin, name, image, created_at, id) values (?,?,?,?,?,?,?)"
        args = (next_email()+'@dummy.com','12345678',True,'fathergod','about:blank','19260817',idd)
        affected_insert = loop.run_until_complete(orm.execute(insert_user,args))
        self.assertEqual(affected_insert,1)

        checked_insert = "select * from users where id=?"
        cond = (idd,)
        result = loop.run_until_complete(orm.select(checked_insert,cond))
        self.assertEqual(len(result),1)
        #print(result)
    
    def test_class_method(self):
        now = datetime.now()
        signature = str(now.minute)
        orm.setDatabase('../www/awesome.db')
        loop = asyncio.get_event_loop()
        test_users = [
            models.User(name=str(time.time()),passwd=signature,email=next_email()+'@dummy.com',image="about:blank",admin=False),
            models.User(name=str(time.time()),passwd=signature,email=next_email()+'@dummy.com',image="about:blank",admin=False),
            models.User(name=str(time.time()),passwd=signature,email=next_email()+'@dummy.com',image="about:blank",admin=False)
        ]

        for u in test_users:
            loop.run_until_complete(u.save())

        inserted = loop.run_until_complete(models.User.findAll('passwd=?',[signature]))
        self.assertEqual(len(inserted),3)

        for u in test_users:
            u.passwd = signature + '1'
            loop.run_until_complete(u.update())
        
        modified = loop.run_until_complete(models.User.findAll('passwd=?',[signature+'1']))
        self.assertEqual(len(modified),3)
        #print(modified)

        for u in test_users:
            loop.run_until_complete(u.remove())

        after = loop.run_until_complete(models.User.findAll('passwd=?',[signature+'1']))
        self.assertEqual(len(after),0)
    
    def test_find(self):
        loop = asyncio.get_event_loop()
        num = loop.run_until_complete(models.User.findNumber('count(*)','email like ?',['%dummy%']))
        #print(num)
        self.assertIsNot(num[0],0)

        res = loop.run_until_complete(models.User.find('0015615749997056198eaebaa0246339e1e1ac3e1883125000'))
        self.assertIsNot(res,None)


if __name__=="__main__":
    unittest.main()


