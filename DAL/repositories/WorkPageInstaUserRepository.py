from sqlalchemy.exc import SQLAlchemyError
import DAL.repositories as repositories
from datetime import datetime, timedelta
from Bot.enums import Actions
from DAL.models import *
import time


class WorkPageInstaUserRepository(repositories.BaseRepository):

    def __init__(self):
        super(WorkPageInstaUserRepository, self).__init__(WorkPageInstaUser)

    def already_followed(self, user, workpage_username):
        user_repository = repositories.InstaUserRepository()
        wp_repository = repositories.WorkPageRepository()
        user, err = user_repository.get(Username=user)
        wp, wp_err = wp_repository.get(Username=workpage_username)
        if user and wp:
            wp_user = self.get(WorkPageId=wp.WORK_PAGE_ID, InstaUserId=user.INSTA_USER_ID)
            if wp_user:
                if wp_user.IsFollowed and wp_user.FollowDateTime:
                    return True
        return False


    def add_follow(self, user, workpage_username, targetpage_username):
        user_repository = repositories.InstaUserRepository()
        wp_repository = repositories.WorkPageRepository()
        tp_repository = repositories.TargetPageRepository()
        insta_user, err = user_repository.get(Username=user.username)
        wp, wp_err = wp_repository.get(Username=workpage_username)
        tp, tp_err = tp_repository.get(Username=targetpage_username)
        if not insta_user:
            insta_user = InstaUser()
            insta_user.Username = user.username
            insta_user.FullName = user.fullname
            insta_user.ImageUrl = user.imageurl
            insta_user.ImageHDUrl = user.imagehdurl
            insta_user.IsDeleted = False
        if wp and tp:
            wp_insta_user = WorkPageInstaUser()
            wp_insta_user.WorkPageId = wp.WORK_PAGE_ID
            wp_insta_user.TargetPageId = tp.TARGET_PAGE_ID
            wp_insta_user.IsFollowed = True
            wp_insta_user.IsUnfollowed = False
            now = time.time()
            wp_insta_user.FollowDateTime = int(now)

            ac_log = repositories.ActionLogRepository.get_action_log(wp, Actions.Follow, now, content_id=insta_user.INSTA_USER_ID, reference=insta_user.Username)

            try:
                with self.session_scope(commit_needed=True) as session:
                    session.add(insta_user)
                    session.flush()
                    wp_insta_user.InstaUserId = insta_user.INSTA_USER_ID
                    session.add(wp_insta_user)
                    ac_log.ContentId = insta_user.INSTA_USER_ID
                    session.add(ac_log)
                return True, None
            except SQLAlchemyError as e:
                return False, "Error occured: " + str(e)

    def set_unfollow(self, insta_user_username, workpage_username):
        user_repository = repositories.InstaUserRepository()
        wp_repository = repositories.WorkPageRepository()
        insta_user, err = user_repository.get(Username=insta_user_username)
        wp, wp_err = wp_repository.get(Username=workpage_username)

        if insta_user and wp:
            try:
                now = int(time.time())
                ac_log = repositories.ActionLogRepository.get_action_log(wp, Actions.UnFollow, now, content_id=insta_user.INSTA_USER_ID, reference=insta_user.Username)
                with self.session_scope(commit_needed=True) as session:
                    session.query(WorkPageInstaUser).filter_by(WorkPageId=wp.WORK_PAGE_ID, InstaUserId=insta_user.INSTA_USER_ID).update({'IsUnfollowed': True, 'UnfollowDateTime': now})
                    session.add(ac_log)
                return True, None
            except SQLAlchemyError as e:
                return False, "Error occurred: " + str(e)

    def set_follow_back(self, workpage_username, user_list):
        user_repository = repositories.InstaUserRepository()
        wp_repository = repositories.WorkPageRepository()
        wp, wp_err = wp_repository.get(Username=workpage_username)

        if wp:
            for username in user_list:
                insta_user, err = user_repository.get(Username=username)
                if insta_user:
                    try:
                        with self.session_scope(commit_needed=True) as session:
                            session.query(WorkPageInstaUser).filter_by(WorkPageId=wp.WORK_PAGE_ID,
                                                                       InstaUserId=insta_user.INSTA_USER_ID).update({'IsFollowBack': True})
                    except SQLAlchemyError as e:
                        print("Error occurred: " + str(e))

            action_log_repository = repositories.ActionLogRepository()
            ac_log = action_log_repository.get_action_log(wp, Actions.GetFollowers)
            action_log_repository.add(ac_log)

