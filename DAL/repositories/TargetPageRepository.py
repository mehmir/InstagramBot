from sqlalchemy.exc import SQLAlchemyError

from DAL.repositories import BaseRepository
from DAL.models import *


class TargetPageRepository(BaseRepository):

    def __init__(self):
        super(TargetPageRepository, self).__init__(TargetPage)

    def update_target_page_info(self, page_info):
        try:
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
            with self.session_scope(commit_needed=True) as session:
                session.query(TargetPage).filter_by(Username=page_info.username).update(update_info)
            return True, None
        except SQLAlchemyError as e:
            return False, "Error occurred: " + str(e)
