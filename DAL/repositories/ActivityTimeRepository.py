from DAL.repositories import BaseRepository
from DAL.models import *


class ActivityTimeRepository(BaseRepository):

    def __init__(self):
        super(ActivityTimeRepository, self).__init__(ActivityTime)
