from DAL.repositories import BaseRepository
from DAL.models import *


class InstaUserRepository(BaseRepository):

    def __init__(self):
        super(InstaUserRepository, self).__init__(InstaUser)



