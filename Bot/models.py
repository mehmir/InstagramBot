from Bot.enums import PostTypes
import Bot.bot_config as config


class Post:

    def __init__(self, element, url, type = PostTypes.Image):
        self.element = element
        self.url = url
        self.type = type
        self.post_id = url.split(config.instaBaseLink)[-1]
        self.likes = 0
        self.comments = 0
        self.views = 0

    def set_type(self, type):
        self.type = type

    def set_stats(self, comments, likes=0, views=0):
        self.comments = comments
        self.likes = likes
        self.views = views


class User:

    def __init__(self, url, fullname='', imageurl='', imagehdurl=''):
        self.fullname = fullname
        self.url = url
        self.username = url.strip('/').split('/')[-1]
        self.imageurl = imageurl
        self.imagehdurl = imagehdurl

    def __eq__(self, other):
        return self.username == other.username


class InstaComment:

    def __init__(self, insta_id, comment, post_id, username, url):
        self.comment_id = insta_id
        self.comment = comment
        self.post_id = post_id
        self.username = username
        self.comment_url = url


class PageInfo:
    def __init__(self, username, followers, following, full_name, post_count, image, image_hd, id):
        self.username = username
        self.followers = followers
        self.following = following
        self.full_name = full_name
        self.post_count = post_count
        self.image = image
        self.image_hd = image_hd
        self.id = id