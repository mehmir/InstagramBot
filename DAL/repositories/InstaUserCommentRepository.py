from sqlalchemy.exc import SQLAlchemyError

from DAL.repositories import BaseRepository
from DAL import repositories
from DAL.models import *


class InstaUserCommentRepository(BaseRepository):

    def __init__(self):
        super(InstaUserCommentRepository, self).__init__(InstaUserComment)

    def add_comment(self, user, comment, targetpage_username):
        user_repository = repositories.InstaUserRepository()
        insta_user, err = user_repository.get(Username=user.username)
        user_not_exist = insta_user is None
        tp_repository = repositories.TargetPageRepository()
        tp, err = tp_repository.get(Username=targetpage_username)
        if tp:
            if user_not_exist:
                insta_user = InstaUser()
                insta_user.Username = user.username
                insta_user.FullName = user.fullname
                insta_user.ImageHDUrl = user.imagehdurl
                insta_user.ImageUrl = user.imageurl
                insta_user.Url = user.url
                insta_user.IsDeleted = False

            try:
                with self.session_scope(commit_needed=True) as session:
                    if user_not_exist:
                        session.add(insta_user)
                        session.flush()
                    comment = self.get_insta_comment(insta_user, comment, tp)
                    session.add(comment)
                    insta_user_source = session.query(InstaUserSource).filter_by(InstaUserId=insta_user.INSTA_USER_ID, TargetPageId=tp.TARGET_PAGE_ID).one_or_none()
                    if not insta_user_source:
                        insta_user_source = InstaUserSource()
                        insta_user_source.TargetPageId = tp.TARGET_PAGE_ID
                        insta_user_source.InstaUserId = insta_user.INSTA_USER_ID
                        insta_user_source.Source = UserSource.Comments
                        session.add(insta_user_source)
                    else:
                        session.query(InstaUserSource).filter_by(InstaUserId=insta_user.INSTA_USER_ID,
                                                                 TargetPageId=tp.TARGET_PAGE_ID).update({'Source': UserSource.Comments})
            except SQLAlchemyError as e:
                print("Error occurred: " + str(e))

    @staticmethod
    def get_insta_comment(insta_user, insta_comment, targetpage):
        comment = InstaUserComment()
        comment.TargetPageId = targetpage.TARGET_PAGE_ID
        comment.InstaUserId = insta_user.INSTA_USER_ID
        comment.InstaCommentId = insta_comment.comment_id
        comment.InstaPostId = insta_comment.post_id
        comment.InstaUser_Username = insta_user.Username
        comment.CommentText = insta_comment.comment
        comment.CommentUrl = insta_comment.comment_url
        comment.TargetPageId = targetpage.TARGET_PAGE_ID
        return comment
