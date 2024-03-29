class Page(object):

    def __init__(self, item_count, page_index=1, page_size=8):
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)
        if (item_count == 0) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__

def get_page_index(page_idx,page_size='8'):
    try:
        num = int(page_idx)
        page_size = int(page_size)
        if num >=1 and page_size>=1:
            return num,page_size
        else:
            raise APIValueError('Invalid Parameter:\'page\'')
    except:
        raise APIValueError('Invalid Parameter:\'page\'')

class APIError(Exception):
    def __init__(self,error,data='',message=''):
        super(APIError,self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    The input value is invalid
    '''
    def __init__(self,field,message=''):
        super(APIValueError,self).__init__('value:invalid',field,message)

class APIResourceNotFoundError(APIError):
    '''
    Cannot found the required resource
    '''
    def __init__(self,field,message=''):
        super(APIResourceNotFoundError,self).__init__('value:not found',field,message)

class APIPermissionError(APIError):
    '''
    Not permitted
    '''
    def __init__(self,field,message=''):
        super(APIPermissionError,self).__init__('permission:forbidden',field,message)
