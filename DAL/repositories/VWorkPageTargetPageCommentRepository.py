from DAL.repositories import BaseRepository
from DAL import repositories
from DAL.models import *


class VWorkPageTargetPageCommentRepository(BaseRepository):

    def __init__(self):
        super(VWorkPageTargetPageCommentRepository, self).__init__(VWorkPageTargetPageComment)

    def get_comments(self, workpage_username, targetpage_username):
        wp_repository = repositories.WorkPageRepository()
        tp_repository = repositories.TargetPageRepository()
        wp, wp_err = wp_repository.get(Username=workpage_username)
        tp, tp_err = tp_repository.get(Username=targetpage_username)

        if wp and tp:
            comments, err = self.where(VWorkPageTargetPageComment.WorkPageId == wp.WORK_PAGE_ID, VWorkPageTargetPageComment.TargetPageId == tp.TARGET_PAGE_ID)
            comments = [comment for comment in comments if comment]
            return comments
