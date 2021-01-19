from DAL.repositories import BaseRepository
from DAL.models import *


class VWorkpageTargetpageRepository(BaseRepository):

    def __init__(self):
        super(VWorkpageTargetpageRepository, self).__init__(VWorkPageTargetPage)

    def get_target_pages(self, workpage):
        wp_targets, err = self.where(VWorkPageTargetPage.WorkPageId == workpage.WORK_PAGE_ID)
        if not err:
            return [wp_tp.Username for wp_tp in wp_targets if wp_tp]
        else:
            return []
