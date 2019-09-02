# coding:utf-8
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, create_engine, VARCHAR,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from config import DB_CONFIG, DEFAULT_SCORE
from db.ISqlHelper import ISqlHelper
from sqlalchemy.engine import create_engine
'''
sql操作的基类
ip池建表字段：
    id(主键)
    ip（ip号）
    port（端口号）
    t_way(免费/付费)
    protocol（0：http,1:https,2:http/https）
    country(国内/国外)
    addr(城市代码)
    t_service(服务类型,电信/联通/移动)
    usable_time（采集时间+时效）
    Update_time（检测时间）
    score（可被取用次数）
    attr(属性，0：采集未检测，1：采集并检测)
'''
BaseModel = declarative_base()
class Speed(BaseModel):
    __tablename__ = 'speed'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_id=Column(Integer, ForeignKey('proxys.id', ondelete='CASCADE'),nullable=False)
    speed = Column(Numeric(5, 2), nullable=False)
    sp_proxys = relationship('Proxy', backref='sp_proxys')



class Proxy(BaseModel):
    __tablename__ = 'proxys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    port = Column(Integer, nullable=False)
    t_way = Column(Integer, nullable=False)
    protocol = Column(Integer, nullable=False, default=0)
    country = Column(VARCHAR(20), nullable=False)
    addr = Column(VARCHAR(100), nullable=False)
    t_service = Column(VARCHAR(100), nullable=False)
    usable_time = Column(DateTime())
    update_time = Column(DateTime(), default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    score = Column(Integer, nullable=False, default=DEFAULT_SCORE)
    attr=Column(Integer, nullable=False,default=0)
class SqlHelper(ISqlHelper):
    params = {'ip': Proxy.ip, 'port': Proxy.port, 't_way ':Proxy.t_way ,'protocol': Proxy.protocol,'country': Proxy.country, 'addr':Proxy.addr,'t_service':Proxy.t_service, 'usable_time':Proxy.usable_time,'update_time':Proxy.update_time,'score': Proxy.score,'attr':Proxy.attr}
    def __init__(self):
        if 'sqlite' in DB_CONFIG['DB_CONNECT_STRING']:
            connect_args = {'check_same_thread': False}
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False, connect_args=connect_args)
        else:
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False)
        DB_Session = sessionmaker(bind=self.engine)
        self.session = DB_Session()
    def init_db(self):
        BaseModel.metadata.create_all(self.engine)
    def drop_db(self):
        BaseModel.metadata.drop_all(self.engine)
    def insert(self,value):
        proxy = Proxy(ip=value['ip'], port=value['port'], t_way=value['t_way'], protocol=value['protocol'],country=value['country'],addr=value['addr'], t_service=value['t_service'],attr=value['attr'])
        self.session.add(proxy)
        self.session.commit()
    def delete(self, conditions=None):
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            deleteNum = query.delete()
            self.session.commit()
        else:
            deleteNum = 0
        return ('deleteNum', deleteNum)
    def update(self, conditions=None, value=None):
        if conditions and value:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            updatevalue = {}
            for key in list(value.keys()):
                if self.params.get(key, None):
                    updatevalue[self.params.get(key, None)] = value.get(key)
            updateNum = query.update(updatevalue)
            self.session.commit()
        else:
            updateNum = 0
        return {'updateNum': updateNum}
    def select(self, count=None, conditions=None):
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
        else:
            conditions = []
        query = self.session.query(Proxy.ip, Proxy.port, Proxy.score)
        if len(conditions) > 0 and count:
            for condition in conditions:
                query = query.filter(condition)
            return query.order_by(Proxy.score.desc(), Proxy.speed).limit(count).all()
        elif count:
            return query.order_by(Proxy.score.desc(), Proxy.speed).limit(count).all()
        elif len(conditions) > 0:
            for condition in conditions:
                query = query.filter(condition)
            return query.order_by(Proxy.score.desc(), Proxy.speed).all()
        else:
            return query.order_by(Proxy.score.desc(), Proxy.speed).all()
    def close(self):
        pass
if __name__ == '__main__':
    sqlhelper = SqlHelper()
    sqlhelper.init_db()
    proxy = {'ip': '192.168.1.1', 'port': 80, 'type': 0, 'protocol': 0, 'country': '中国', 'area': '广州', 'speed': 11.123, 'types': ''}
    sqlhelper.insert(proxy)
    sqlhelper.update({'ip': '192.168.1.1', 'port': 80}, {'score': 10})
    print(sqlhelper.select(1))