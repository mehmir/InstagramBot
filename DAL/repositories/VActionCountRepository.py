from DAL.repositories import BaseRepository, WorkPageRepository
from DAL.models import *


class VActionCountRepository(BaseRepository):

    def __init__(self):
        super(VActionCountRepository, self).__init__(VActionCount)

    def get_action_count(self, workpage_username, time):
        repository = WorkPageRepository()
        wp, err = repository.get_workpage_by_username(workpage_username)
        action_counts = []
        if wp:
            day, hour = ActionLog.get_day_hour(time)
            action_counts, err = self.where(VActionCount.Day == day, VActionCount.WorkPageId == wp.WORK_PAGE_ID)
            # daycount = 0
            # hourcount = 0
            # for item in action_counts:
            #     if item.Hour == hour:
            #         hourcount += item.Count
            #     daycount += item.Count

        return action_counts

