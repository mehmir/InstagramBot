from sqlalchemy.exc import SQLAlchemyError

from DAL.repositories import BaseRepository
from DAL.models import *


class WorkPageRepository(BaseRepository):

    def __init__(self):
        super(WorkPageRepository, self).__init__(WorkPage)

    def get_workpage_by_username(self, username):
        wp = self.get(Username=username)
        return wp

    def get_admin_workpages(self):
        wps = self.where(WorkPage.CustomerId==0)
        return wps

    def update_status(self, username, status):
        wp, _ = self.get_workpage_by_username(username)
        if wp:
            try:
                with self.session_scope(commit_needed=True) as session:
                    session.query(WorkPage).filter_by(WORK_PAGE_ID=wp.WORK_PAGE_ID).update({'Status': status})
                return True, None
            except SQLAlchemyError as e:
                return False, "Error occurred: " + str(e)

