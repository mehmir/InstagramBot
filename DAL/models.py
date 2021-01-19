from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mssql import BIGINT, BIT
from sqlalchemy.types import Enum, TypeDecorator, Integer as typeInteger
import datetime
from Bot.enums import Actions, UserSource, WorkPageStatus

Base = declarative_base()


class IntEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = typeInteger

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class InstaUser(Base):
    __tablename__ = 'INSTA_USER'
    INSTA_USER_ID = Column(BIGINT, primary_key=True)
    Username = Column(String)
    FullName = Column(String)
    Url = Column(String)
    ImageUrl = Column(String)
    ImageHDUrl = Column(String)
    IsDeleted = Column(BIT)


class TargetPage(Base):
    __tablename__ = 'TARGET_PAGE'
    TARGET_PAGE_ID = Column(BIGINT, primary_key=True)
    Username = Column(String)
    InstagramId = Column(BIGINT)
    ImageUrl = Column(String)
    ImageHDUrl = Column(String)
    FollowerCount = Column(Integer)
    FollowingCount = Column(Integer)
    PostCount = Column(Integer)
    FullName = Column(String)
    IsDeleted = Column(BIT)


class VWorkPageTargetPage(Base):
    __tablename__ = 'V_WORK_PAGE_TARGET_PAGE'
    TargetPageId = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT, primary_key=True)
    Username = Column(String)
    InstagramId = Column(BIGINT)
    ImageUrl = Column(String)
    ImageHDUrl = Column(String)
    FollowerCount = Column(Integer)
    FollowingCount = Column(Integer)
    PostCount = Column(Integer)
    FullName = Column(String)


class WorkPage(Base):
    __tablename__ = 'WORK_PAGE'
    WORK_PAGE_ID = Column(BIGINT, primary_key=True)
    Username = Column(String)
    Password = Column(String)
    FullName = Column(String)
    CustomerId = Column(BIGINT)
    ProxyId = Column(BIGINT)
    FollowerCount = Column(Integer)
    FollowingCount = Column(Integer)
    PostCount = Column(Integer)
    ImageUrl = Column(String)
    ImageHDUrl = Column(String)
    InstagramId = Column(BIGINT)
    IsDeleted = Column(BIT)
    Status = Column(IntEnum(WorkPageStatus))
    # Status = Column(Integer)


class Comment(Base):
    __tablename__ = 'COMMENT'
    COMMENT_ID = Column(BIGINT, primary_key=True)
    ContentText = Column(String)
    WorkPageId = Column(BIGINT)
    IsDeleted = Column(BIT)


class Config(Base):
    __tablename__ = 'CONFIG'
    ConfigKey = Column(Integer, primary_key=True)
    ContentText = Column(String)
    WorkPageId = Column(BIGINT)
    IsDeleted = Column(BIT)


class Proxy(Base):
    __tablename__ = 'PROXY'
    PROXY_ID = Column(BIGINT, primary_key=True)
    Address = Column(String)
    Port = Column(Integer)
    Username = Column(String)
    Password = Column(String)
    Country = Column(String)


class WorkPageInstaUser(Base):
    __tablename__ = 'WORK_PAGE_INSTA_USER'
    WORK_PAGE_INSTA_USER_ID = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT)
    InstaUserId = Column(BIGINT)
    TargetPageId = Column(BIGINT)
    IsFollowed = Column(BIT)
    IsUnfollowed = Column(BIT)
    IsFollowBack = Column(BIT)
    FollowDateTime = Column(BIGINT)
    UnfollowDateTime = Column(BIGINT)


class VWorkPageInstaUser(Base):
    __tablename__ = 'V_WORK_PAGE_INSTA_USER'
    WORK_PAGE_INSTA_USER_ID = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT)
    InstaUserId = Column(BIGINT)
    TargetPageId = Column(BIGINT)
    IsFollowed = Column(BIT)
    IsUnfollowed = Column(BIT)
    IsFollowBack = Column(BIT)
    FollowDateTime = Column(BIGINT)
    UnfollowDateTime = Column(BIGINT)
    InstaUser_Username = Column(String)
    Workpage_Username = Column(String)


class WorkPageTargetPage(Base):
    __tablename__ = 'WORK_PAGE_TARGET_PAGE'
    WORK_PAGE_TARGET_PAGE_ID = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT)
    TargetPageId = Column(BIGINT)
    IsDeleted = Column(BIT)


class WorkPageTargetPageComment(Base):
    __tablename__ = 'WORK_PAGE_TARGET_PAGE_COMMENT'
    WORK_PAGE_TARGET_PAGE_COMMENT_ID = Column(BIGINT, primary_key=True)
    WorkPageTagetPageId = Column(BIGINT)
    CommentId = Column(BIGINT)
    IsDeleted = Column(BIT)


class Setting(Base):
    __tablename__ = 'SETTING'
    SETTING_ID = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT)
    MaxLikePostsPerHour = Column(Integer)
    MaxLikePostsPerDay = Column(Integer)
    MaxLikeCommentsPerHour = Column(Integer)
    MaxLikeCommentsPerDay = Column(Integer)
    MaxLikeOldPostsPerPage = Column(Integer)
    MaxLikeCommentsPerPost = Column(Integer)
    MaxFollowsPerHour = Column(Integer)
    MaxFollowsPerDay = Column(Integer)
    MaxFollowPerPage = Column(Integer)
    MaxUnfollowsPerHour = Column(Integer)
    MaxUnfollowsPerDay = Column(Integer)
    UnfollowAfterDays = Column(Integer)
    MaxCommentPerHour = Column(Integer)
    MaxCommentPerDay = Column(Integer)
    MaxCommentPerPost = Column(Integer)
    IgnoreFollowers = Column(BIT)
    EnableLikePosts = Column(BIT)
    EnableLikeComments = Column(BIT)
    EnableFollow = Column(BIT)
    EnableUnFollow = Column(BIT)
    EnableComments = Column(BIT)
    IsDeleted = Column(BIT)


class ActionLog(Base):
    __tablename__ = 'ACTION_LOG'
    ACTION_LOG_ID = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT)
    ActionType = Column(IntEnum(Actions))
    Reference = Column(String)
    ContentId = Column(BIGINT)
    ActionDateTime = Column(BIGINT)
    Day = Column(Integer)
    Hour = Column(Integer)

    @staticmethod
    def get_day_hour(time_now):
        dt = datetime.datetime.fromtimestamp(time_now)
        day = int(str(dt.date()).replace('-', ''))
        hour = dt.hour
        return day, hour


class VActionCount(Base):
    __tablename__ = 'V_ACTION_COUNT'
    Id = Column(Integer, primary_key=True)
    WorkPageId = Column(BIGINT)
    ActionType = Column(IntEnum(Actions))
    Day = Column(Integer)
    Hour = Column(Integer)
    Count = Column(Integer)


class VWorkPageTargetPageComment(Base):
    __tablename__ = 'V_WORK_PAGE_TARGET_PAGE_COMMENT'
    WORK_PAGE_TARGET_PAGE_COMMENT_ID = Column(BIGINT, primary_key=True)
    WorkPageTagetPageId = Column(BIGINT)
    WorkPageId = Column(BIGINT)
    TargetPageId = Column(BIGINT)
    CommentId = Column(BIGINT)
    ContentText = Column(String)


class InstaUserComment(Base):
    __tablename__ = 'INSTA_USER_COMMENT'
    INSTA_USER_COMMENT_ID = Column(BIGINT, primary_key=True)
    InstaUserId = Column(BIGINT)
    InstaCommentId = Column(String)
    InstaPostId = Column(String)
    CommentUrl = Column(String)
    TargetPageId = Column(BIGINT)
    InstaUser_Username = Column(String)
    CommentText = Column(String)


class InstaUserSource(Base):
    __tablename__ = 'INSTA_USER_SOURCE'
    INSTA_USER_SOURCE_ID = Column(BIGINT, primary_key=True)
    InstaUserId = Column(BIGINT)
    TargetPageId = Column(BIGINT)
    Source = Column(IntEnum(UserSource))


class ActivityTime(Base):
    __tablename__ = 'ACTIVITY_TIME'
    ACTIVITY_TIME_ID = Column(BIGINT, primary_key=True)
    WorkPageId = Column(BIGINT)
    StartTime = Column(String)
    EndTime = Column(String)
    Days = Column(Integer)
    IsDeleted = Column(BIT)
