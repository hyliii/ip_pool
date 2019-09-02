# coding:utf-8
class ISqlHelper(object):
    params = {'ip':None, 'port': None, 't_way ':None ,'protocol': None,'country': None, 'addr':None,'t_service':None, 'usable_time':None,'update_time':None,'score': None,'attr':None}
    def init_db(self):
        raise NotImplemented
    def drop_db(self):
        raise NotImplemented
    def insert(self, value=None):
        raise NotImplemented
    def delete(self, conditions=None):
        raise NotImplemented
    def update(self, conditions=None, value=None):
        raise NotImplemented
    def select(self, count=None, conditions=None):
        raise NotImplemented