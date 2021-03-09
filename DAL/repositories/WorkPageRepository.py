from sqlalchemy.exc import SQLAlchemyError

from DAL.repositories import BaseRepository
from DAL.models import *


class WorkPageRepository(BaseRepository):

    def __init__(self):
        super(WorkPageRepository, self).__init__(WorkPage)

    def get_workpage_by_username(self, username):
        wp = self.get(Username=username, IsDeleted=False)
        return wp

    def get_admin_workpages(self):
        wps = self.where(WorkPage.CustomerId==0)
        return wps

    def update(self, username, status, page_info):
        wp, _ = self.get_workpage_by_username(username)
        if wp:
            update_info = {}
            if page_info:
                update_info = {
                    'InstagramId': page_info.id,
                    'ImageUrl': page_info.image,
                    'ImageHDUrl': page_info.image_hd,
                    'FollowerCount': page_info.followers,
                    'FollowingCount': page_info.following,
                    'PostCount': page_info.post_count,
                    'FullName': page_info.full_name,
                    'UpdateInfoStatus': 2
                }
            if status:
                update_info.update({'Status': status})
            if update_info:
                try:
                    with self.session_scope(commit_needed=True) as session:
                        session.query(WorkPage).filter_by(WORK_PAGE_ID=wp.WORK_PAGE_ID).update(update_info)
                    return True, None
                except SQLAlchemyError as e:
                    return False, "Error occurred: " + str(e)

