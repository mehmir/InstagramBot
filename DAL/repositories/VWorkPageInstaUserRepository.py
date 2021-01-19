from sqlalchemy.exc import SQLAlchemyError
import DAL.repositories as repositories
from datetime import datetime, timedelta
from Bot.enums import Actions
from DAL.models import *
import time


class VWorkPageInstaUserRepository(repositories.BaseRepository):

    def __init__(self):
        super(VWorkPageInstaUserRepository, self).__init__(VWorkPageInstaUser)

    def get_unfollow_list(self, workpage_username, duration):
        d = datetime.datetime.today() - timedelta(days=duration)
        d = int(d.timestamp())
        wp_repository = repositories.WorkPageRepository()
        wp, wp_err = wp_repository.get(Username=workpage_username)
        lst=[]
        if wp:
            lst, err = self.where(VWorkPageInstaUser.FollowDateTime < d, VWorkPageInstaUser.WorkPageId == wp.WORK_PAGE_ID)
            return [item.InstaUser_Username for item in lst]

        return lst

