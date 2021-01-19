import enum

import sqlalchemy.types as db

JS_ADD_TEXT_TO_INPUT = """
  var element = arguments[0], txt = arguments[1];
  element.value += txt;
  element.dispatchEvent(new Event('change'));
  """


class Constants:
    js_add_text_to_input = """
      var element = arguments[0], txt = arguments[1];
      element.value += txt;
      element.dispatchEvent(new Event('change'));
      """


class BotErrors(enum.Enum):
    Unknown = 0
    Login_Failed = 1
    Pass_Incorrect = 2
    Internet_Problems = 3
    Not_Available = 4
    InstaError = 5
    InstaBlock = 6
    InstaTry = 7
    InstaNotLoadList = 8
    InstaCommentBlocked = 9
    InstaTempLocked = 10
    User_Incorrect = 11
    Couldnt_Connet_Insta = 12


class PostTypes(enum.Enum):
    Image = 1
    MultiImage = 2
    Video = 3


class Browser(enum.Enum):
    Chrome = 1
    Firefox = 2


class Tabs(enum.Enum):
    GetFollowers = 0
    Follow = 1
    Unfollow = 2
    Comment = 3
    FollowLikers = 4


class Actions(enum.Enum):
    LikePost = 1
    CommentPost = 2
    Follow = 3
    UnFollow = 4
    LikeComment = 5
    GetFollowers = 6


class UserSource(enum.Enum):
    Followers = 1
    Likes = 2
    Comments = 3


class WeekDay(enum.IntFlag):
    Nothing = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 4
    Thursday = 8
    Friday = 16
    Saturday = 32
    Sunday = 64


class WorkPageStatus(enum.Enum):
    Verified = 1
    WrongUsername = 2
    WrongPassword = 3
    Pendding = 4
    TempLocked = 5
    Unknown = 6
