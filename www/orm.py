import asyncio, logging, aiosqlite

def log(sql,args=()):
    logging.info("sql: {}".format(sql))



DATABASE = "awesome.db"

def setDatabase(database):
    global DATABASE
    DATABASE = database


async def select(sql,args,size=None):
    log(sql)
    global DATABASE
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(sql,args) as cursor:
            if size:
                rs = await cursor.fetchmany(size)
            else:
                rs = await cursor.fetchall()
        logging.info("rows returned, len={}".format(len(rs)))
        return rs

async def execute(sql,args):
    log(sql)
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(sql,args)
        await db.commit()
        affected = db.total_changes
        return affected


def create_args_string(num):
    L = []
    for _ in range(num):
        L.append('?')
    return ', '.join(L)

class ModelMetaClass(type):
    '''
    metaclass to dynamically define a model class
    1. scan attributes dict, if find a match to a field, then append it to the mappings list,
        scan and check for the unique primary key.
    2. delete matched attributes from attributes dict
    3. set reserved keywords : __table__, __mapping__, __fields__, __primary_key__
    4. construct default queries
    '''
    def __new__(cls,name,bases,attrs):
        if name=="Model":
            return type.__new__(cls,name,bases,attrs)
        tableName = attrs.get("__table__",None) or name
        logging.info("found model: {} (table: {})".format(name,tableName))
        mappings = dict()
        fields = []
        primary_key = None
        for key,value in attrs.items():
            if isinstance(value,Field):
                logging.info("found mapping: {} ==> {}".format(key,value))
                mappings[key] = value 
                if value.primary_key:
                    #found primary key
                    if primary_key:
                        raise RuntimeError("Error: duplicated primary key: {} ,{}".format(primary_key,key))
                    primary_key = key
                else:
                    fields.append(key)
        if not primary_key:
            raise RuntimeError("Error: cannot find primary key")
        for key in mappings.keys():
            attrs.pop(key)
        
        escaped_fields = list(map(lambda f:"{}".format(f),fields))
        attrs["__mapping__"] = mappings
        attrs["__primary_key__"] = primary_key
        attrs["__fields__"] = fields
        attrs["__table__"] = tableName

        """
        construct default INSERT, DELETE, UPDATE, SELECT queries
        """
        attrs["__select__"] = "SELECT {}, {} FROM {}".format(primary_key,', '.join(escaped_fields),tableName)
        attrs["__insert__"] = "INSERT INTO {} ({},{}) VALUES ({})".format(
            tableName,
            ', '.join(escaped_fields),
            primary_key,
            create_args_string(len(escaped_fields)+1))
        attrs['__update__'] = "UPDATE {} SET {} WHERE {}=?".format(
            tableName,
             ', '.join(map(lambda f: '{}=?'.format(mappings.get(f).name or f),fields)),
             primary_key)
        attrs['__delete__'] = "DELETE FROM {} WHERE {}=?".format(tableName, primary_key)
        return type.__new__(cls, name, bases, attrs)


class Model(dict,metaclass=ModelMetaClass):

    def __init__(self,**kw):
        super(Model,self).__init__(**kw)

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("Fatal Error: cannot find attribute {} in the {} instantce".format(key,self.__class__.__name__))
    
    def __setattr__(self,key,value):
        self[key] = value

    def getValue(self,key):
        return getattr(self,key,None)

    def getValueOrDefault(self,key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mapping__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug("Warning: Using {} for keyword: {}".format(value,key))
                setattr(self,key,value)
        return value
    
    @classmethod
    def convert2dict(cls,args):
        schema = getattr(cls,'__schema__',None)
        kwargs = {}
        if schema:
            for k,v in zip(schema,args):
                kwargs[k] = v
            return kwargs
        else:
            raise Exception('Undefined schema for {}'.format(cls.__table__))


    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ## find objects by where clause
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return list(map(lambda x:cls(**cls.convert2dict(x)),rs))
        #return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ## find number by select and where
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        #rs = cls.convert2dict(rs[0])
        return rs[0][0]

    @classmethod
    async def find(cls, pk):
        ## find object by primary key
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**cls.convert2dict(rs[0]))


    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)


class Field(object):

    def __init__(self,name,primary_key,column_type,default):
        self.name = name
        self.primary_key = primary_key
        self.column_type = column_type
        self.default = default

    def __str__(self):
        return "<{},{}: {}>".format(self.__class__.__name__,self.column_type,self.name)

class IntegerField(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,primary_key,"bigint",default)

class StringField(Field):
    def __init__(self,name=None,primary_key=False,ddl="varchar(100)",default=None):
        super().__init__(name,primary_key,ddl,default)

class BooleanField(Field):
    def __init__(self,name=None,default=False):
        super().__init__(name,False,"boolean",default)

class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=0.0):
        super().__init__(name,primary_key,"real",default)

class TextField(Field):
    def __init__(self,name=None,default=None):
        super().__init__(name,False,"text",default)
