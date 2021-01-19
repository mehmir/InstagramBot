from DAL.repositories import BaseRepository
from DAL.models import *
import time


class ProxyRepository(BaseRepository):

    def __init__(self):
        super(ProxyRepository, self).__init__(Proxy)

    def add_proxy(self, porxy_list):
        list = []
        for proxy in porxy_list:
            ip, port, username, password, country = proxy
            new_proxy = Proxy()
            new_proxy.Country = country
            new_proxy.Port = port
            new_proxy.Address = ip
            new_proxy.Username = username
            new_proxy.Password = password
            list.append(new_proxy)
        self.add(*list)
