from sqlalchemy.exc import SQLAlchemyError
from DAL.repositories import BaseRepository
from DAL.models import *
import time


class ActionLogRepository(BaseRepository):

    def __init__(self):
        super(ActionLogRepository, self).__init__(ActionLog)

    def get_action_log_count(self, workpage_id, action, reference):
        results, _ = self.where(ActionLog.WorkPageId==workpage_id, ActionLog.ActionType==action, ActionLog.Reference==reference)
        if results:
            return len(results)
        return 0

    def get_comentLikePage_count(self, workpage_id, post_id):
        results, _ = self.where(ActionLog.WorkPageId==workpage_id, ActionLog.ActionType==Actions.LikeComment,
                             ActionLog.Reference.like(post_id))
        if results:
            return len(results)
        return 0

    @staticmethod
    def get_action_log(workpage, action, now=None, content_id=None, reference=None):
        ac_log = ActionLog()
        if not now:
            now = time.time()
        ac_log.WorkPageId = workpage.WORK_PAGE_ID
        ac_log.ActionDateTime = int(now)
        ac_log.ContentId = content_id
        ac_log.Reference = reference
        ac_log.ActionType = action
        day, hour = ac_log.get_day_hour(now)
        ac_log.Day = day
        ac_log.Hour = hour
        return ac_log
