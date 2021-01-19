from DAL.repositories import BaseRepository
from DAL.models import *


class SettingRepository(BaseRepository):

    def __init__(self):
        super(SettingRepository, self).__init__(Setting)