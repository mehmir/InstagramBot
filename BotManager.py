from Bot import InstagramBot
from Bot.enums import Tabs
import random
from ActionManager import ActionManager
import time
from Bot.enums import PostTypes, Actions, BotErrors, Browser
import Bot.bot_config as config
from ActionLimitManager import ActionLimitManager
from datetime import datetime, timedelta
from DAL import repositories
import EncryptionTools
import collections
import RunSchedule
from ProxyManager import ProxyManager
import requests

BotActions = collections.namedtuple('BotActions', 'Follow Unfollow FollowLikers Comment')


class BotManager:

    def __init__(self, work_page=None, hide_browser=True):
        self.hide_browser = hide_browser
        self.workPage = work_page
        self.username = 'gabrihcalderon'
        self.password = '773866qQ123'
        if work_page:
            self.username = work_page.Username
            aes = EncryptionTools.AESCipher()
            self.password = aes.decrypt(work_page.Password)
            self.password = '773866!!'
            self.run_schedule = RunSchedule.RunSchedule(work_page)
        self.setting = None
        self.load_settings()
        self.limit_manager = ActionLimitManager(self.username, self.setting)
        self.bot = None
        self.bot_actions = None
        self.is_running = False
        self.list_of_action_function = []

    def start(self):

        #bot = InstagramBot('nazissanad1', '773866qQ123!', False)
        while True:

            if not self.is_running:
                success = self.initialize_bot()
                if not success:
                    return

            for func in self.list_of_action_function:
                self.load_settings()
                self.limit_manager.set_limits(self.setting)
                if self.run_schedule.can_run():
                    func()
                else:
                    next_run, wait_seconds = self.run_schedule.next_run_time()
                    # wait_seconds = next_run.total_seconds()
                    self.is_running = False
                    self.bot.close()
                    print('bot sleep until {}'.format(next_run.time()))
                    time.sleep(wait_seconds)
                    break

            # self.get_followers_action()
            # self.follow_action()
            # self.unfollow_action()
            # self.comment_action()
            # self.like_and_follow_likers()
            #
            min_wait = self.get_sleep_time(self.bot_actions) - int(time.time())
            wait_time = max(10, min_wait)
            time.sleep(wait_time)

    def initialize_bot(self):
        proxy = self.get_proxy()
        # proxy_manager = ProxyManager(proxy.Address, proxy.Port, proxy.Username, proxy.Password)
        # plugin_file = proxy_manager.get_plugin_file()
        # if not plugin_file:
        #     print('proxy not found for workpage: {}'.format(self.workPage.Username))
        if not InstagramBot.cookie_exist(self.username) and self.hide_browser:
            self.bot_temp = InstagramBot(self.username, self.password, False, proxy=proxy)
            success, err = self.bot_temp.open()
            self.bot_temp.close()
            del self.bot_temp
            if not success:
                print('bot is closed.\nError:', err)
                return False

        self.bot = InstagramBot(self.username, self.password, self.hide_browser, proxy=proxy)

        success, err = self.bot.open()
        if not success:
            print('bot is closed.\nError:', err)
            return False

        self.bot.create_tabs()

        if self.setting:
            follow_action = ActionManager(self.follow_form_tagets(), self.setting.MaxFollowsPerHour)
            unfollow_action = ActionManager(self.unfollow(), self.setting.MaxUnfollowsPerHour)
            follow_likers_action = ActionManager(self.like_and_follow_likers(), self.setting.MaxLikePostsPerHour)
            comment_action = ActionManager(self.commenter_and_like_comments(), self.setting.MaxCommentPerHour)
        else:
            follow_action = ActionManager(self.follow_form_tagets(), 20)
            unfollow_action = ActionManager(self.unfollow(), 20)
            follow_likers_action = ActionManager(self.like_and_follow_likers(), 30)
            comment_action = ActionManager(self.commenter_and_like_comments(), 10)

        self.bot_actions = BotActions(Follow=follow_action, Unfollow=unfollow_action, FollowLikers=follow_likers_action,
                                      Comment=comment_action)
        self.list_of_action_function = [self.get_followers_action, self.follow_action, self.unfollow_action, self.comment_action, self.follow_likers_action]
        self.is_running = True
        return True

    def get_followers_action(self):
        try:
            if self.limit_manager.can_do_action(Actions.GetFollowers):
                if self.bot.is_tab_open(Tabs.GetFollowers):
                    self.bot.switch_to_tab(Tabs.GetFollowers)
                else:
                    self.bot.open_tab(Tabs.GetFollowers)
                self.get_insert_followers()
                self.limit_manager.set_action_count(Actions.GetFollowers, 1)
            else:
                self.bot.close_tab(Tabs.GetFollowers)

        except Exception as e:
            print(e)

    def follow_action(self):
        if self.setting.EnableFollow:
            if self.bot.is_tab_open(Tabs.Follow):
                self.bot.switch_to_tab(Tabs.Follow)
            else:
                self.bot.open_tab(Tabs.Follow)
            try:
                run_count = self.bot_actions.Follow.run_count()
                print('follow count:', run_count)
                for i in range(run_count):
                    if self.limit_manager.can_do_action(Actions.Follow):
                        user, error = self.bot_actions.Follow.next()
                        if user is not None and error is None:
                            print(f'{self.get_date_time(time.time())}:', user.username, 'is Followed')
                            self.limit_manager.set_action_count(Actions.Follow, 1)
                        if error == BotErrors.InstaBlock or error == BotErrors.InstaTry:
                            self.bot_actions.Follow.set_action(self.follow_form_tagets(), is_blocked=True)
                            break
                    else:
                        self.bot_actions.Follow.set_next_run(minute=15)
                        hour, day = self.limit_manager.get_action_count(Actions.Follow)
                        print(f'cannot follow, hour_count: {hour}, day_count: {day}')
                        break
                print('follow nex run:', self.get_date_time(self.bot_actions.Follow.next_run))
            except StopIteration:
                self.bot_actions.Follow.set_action(self.follow_form_tagets())
        else:
            self.bot.close_tab(Tabs.Follow)

    def unfollow_action(self):
        if self.setting.EnableUnFollow:
            if self.bot.is_tab_open(Tabs.Unfollow):
                self.bot.switch_to_tab(Tabs.Unfollow)
            else:
                self.bot.open_tab(Tabs.Unfollow)
            try:
                run_count = self.bot_actions.Unfollow.run_count()
                print('unfollow count:', run_count)
                for i in range(run_count):
                    if self.limit_manager.can_do_action(Actions.UnFollow):
                        user, error = self.bot_actions.Unfollow.next()
                        if user is not None and error is None:
                            print(f'{self.get_date_time(time.time())}:', user, 'is Unfollowed')
                        elif error == BotErrors.InstaTry or error == BotErrors.InstaBlock or error == BotErrors.InstaNotLoadList:
                            print(f'{int(time.time())}:', error)
                            self.bot_actions.Unfollow.set_action(self.unfollow(), True)
                            break
                    else:
                        self.bot_actions.Unfollow.set_next_run(minute=15)
                        hour, day = self.limit_manager.get_action_count(Actions.UnFollow)
                        print(f'cannot unfollow, hour_count: {hour}, day_count: {day}')
                        break
                print('unfollow nex run:', self.get_date_time(self.bot_actions.Unfollow.next_run))
            except StopIteration:
                self.bot_actions.Unfollow.set_action(self.unfollow())
        else:
            self.bot.close_tab(Tabs.Unfollow)

    def comment_action(self):
        if self.setting.EnableComments or self.setting.EnableLikeComments:
            if self.bot.is_tab_open(Tabs.Comment):
                self.bot.switch_to_tab(Tabs.Comment)
            else:
                self.bot.open_tab(Tabs.Comment)
            try:
                run_count = self.bot_actions.Comment.run_count()
                print('comment count:', run_count)
                for i in range(run_count):
                    if self.limit_manager.can_do_action(Actions.LikeComment):
                        user_comments, error = self.bot_actions.Comment.next()
                        user_count = 0
                        like_count = 0
                        for user_comment in user_comments:
                            user, comment, like = user_comment
                            if user and comment:
                                user_count += 1
                                if like:
                                    like_count += 1
                        print(f'{self.get_date_time(time.time())}:', user_count, ' comments retrieved and', like_count,
                              'is liked')
                        self.limit_manager.set_action_count(Actions.LikeComment, like_count)
                        if error == BotErrors.InstaTry or error == BotErrors.InstaBlock:
                            self.limit_manager.set_action_time(Actions.LikeComment, config.wait_for_already_block)
                    else:
                        self.bot_actions.Comment.set_next_run(minute=15)
                        hour, day = self.limit_manager.get_action_count(Actions.LikeComment)
                        print(f'cannot like comment, hour_count: {hour}, day_count: {day}')
                        break
                print('comment nex run:', self.get_date_time(self.bot_actions.Comment.next_run))

            except StopIteration:
                self.bot_actions.Comment.set_action(self.commenter_and_like_comments())
            except Exception as e:
                self.bot_actions.Comment.set_action(self.commenter_and_like_comments())
                print('error in comment')
        else:
            self.bot.close_tab(Tabs.Comment)

    def follow_likers_action(self):
        if self.setting.EnableLikePosts or self.setting.EnableFollow:
            if self.bot.is_tab_open(Tabs.FollowLikers):
                self.bot.switch_to_tab(Tabs.FollowLikers)
            else:
                self.bot.open_tab(Tabs.FollowLikers)
            try:
                run_count = self.bot_actions.FollowLikers.run_count()
                print('followLikers count:', run_count)
                for i in range(run_count):
                    if self.limit_manager.can_do_action(Actions.Follow):
                        user, error = self.bot_actions.FollowLikers.next()
                        if user is not None and error is None:
                            print(f'{self.get_date_time(time.time())}:', user.username, 'is Followed,       next:',
                                  self.get_date_time(self.bot_actions.Follow.next_run))
                            self.limit_manager.set_action_count(Actions.Follow, 1)
                        if error == BotErrors.InstaBlock or error == BotErrors.InstaTry:
                            self.bot_actions.FollowLikers.set_action(self.like_and_follow_likers(), is_blocked=True)
                            break
                    else:
                        self.bot_actions.FollowLikers.set_next_run(minute=15)
                        hour, day = self.limit_manager.get_action_count(Actions.Follow)
                        print(f'cannot unfollow, hour_count: {hour}, day_count: {day}')
                        break
                print('follow likers nex run:', self.get_date_time(self.bot_actions.FollowLikers.next_run))

            except StopIteration:
                self.bot_actions.FollowLikers.set_action(self.like_and_follow_likers())
        else:
            self.bot.close_tab(Tabs.FollowLikers)

    def follow_form_tagets(self):
        targets = self.get_target_pages()
        random.shuffle(targets)
        for target in targets:
            for user, err in self.bot.follow_followers2(target, self.setting.MaxFollowPerPage):
                if user:
                    repository = repositories.WorkPageInstaUserRepository()
                    repository.add_follow(user, self.username, target)
                yield user, err

    def unfollow(self):
        repository = repositories.VWorkPageInstaUserRepository()
        unfollow_list = repository.get_unfollow_list(self.username, self.setting.UnfollowAfterDays)
        follower_list = []
        for user, err in self.bot.unfollow_following2(unfollow_list, follower_list, self.setting.IgnoreFollowers):
            repository = repositories.WorkPageInstaUserRepository()
            repository.set_unfollow(user, self.username)
            yield user, err

    def like_and_follow_likers(self):
        targets = self.get_target_pages()

        random.shuffle(targets)
        for target in targets:
            posts, errorr = self.bot.get_posts(target, self.setting.MaxLikeOldPostsPerPage)
            for _, post in posts.items():
                is_open = self.bot.open_post(post)
                if is_open:
                    if self.limit_manager.can_do_action(Actions.LikePost) and self.setting.EnableLikePosts:
                        is_like, err = self.bot.like_post(close_after=False)
                        if is_like:
                            self.limit_manager.set_action_count(Actions.LikePost, 1)
                            repository = repositories.ActionLogRepository()
                            log = repository.get_action_log(self.workPage,Actions.LikePost, reference=post.post_id)
                            repository.add(log)
                            print('post ', post.post_id, 'is liked')
                if post.type != PostTypes.Video and self.setting.EnableFollow:
                    for user, err in self.bot.follow_post_likers(self.setting.MaxFollowPerPage):
                        if user:
                            repository = repositories.WorkPageInstaUserRepository()
                            repository.add_follow(user, self.username, target)
                        yield user, err

    def commenter_and_like_comments(self):
        targets = self.get_target_pages()
        wp_tp_cmt_repository = repositories.VWorkPageTargetPageCommentRepository()
        random.shuffle(targets)
        for target in targets:
            posts, errorr = self.bot.get_posts(target, self.setting.MaxLikeOldPostsPerPage)
            if posts:
                for _, post in posts.items():
                    is_open = self.bot.open_post(post)
                    if is_open:
                        comments = wp_tp_cmt_repository.get_comments(self.username, target)
                        random.shuffle(comments)
                        cm = comments[0]
                        now = int(time.time())
                        post_comments_count = self.get_comment_count(post.post_id)
                        if now > self.limit_manager.get_action_time(Actions.CommentPost) and self.limit_manager.can_do_action(Actions.CommentPost) and self.setting.EnableComments and post_comments_count < self.setting.MaxCommentPerPost:
                            is_commented, err = self.bot.comment_post(cm.ContentText, False)
                            if is_commented:
                                print('comment on post (' + str(post.post_id) + ') :', cm.ContentText)
                                self.limit_manager.set_action_count(Actions.CommentPost, 1)
                                self.set_log(self.username, Actions.CommentPost, content_id=cm.CommentId, reference=post.post_id)
                            elif err == BotErrors.InstaCommentBlocked:
                                self.limit_manager.set_action_time(Actions.CommentPost, config.wait_for_block)

                        like_chance = config.like_comments_chance
                        like_count = self.get_commentLike_count(post.post_id)
                        if now < self.limit_manager.get_action_time(Actions.LikeComment) or (not self.setting.EnableLikeComments) or like_count >= self.setting.MaxLikeCommentsPerPost:
                            like_chance = 0

                        max_comments = min(int(post.comments * 0.05), config.max_post_comments)
                        for user_comments, error in self.bot.get_commenters_like_post_comments([], max_comments, like_chance):
                            cmt_repository = repositories.InstaUserCommentRepository()
                            for user, cmt, is_liked in user_comments:
                                if is_liked:
                                    self.set_log(self.username, Actions.LikeComment, reference=f'/p/{cmt.post_id}/c/{cmt.comment_id}')
                                cmt_repository.add_comment(user, cmt, target)
                            yield user_comments, error

    def get_sleep_time(self, actions):
        next_runs = [action.next_run for action in actions]
        min_wait = min(next_runs)
        return min_wait

    def get_date_time(self, time):
        dtime = datetime.fromtimestamp(int(time))
        return dtime

    def get_target_pages(self):
        repository = repositories.VWorkpageTargetpageRepository()
        return repository.get_target_pages(self.workPage)

    def get_insert_followers(self):
        followers, err = self.bot.get_followers_profile()
        repository = repositories.WorkPageInstaUserRepository()
        repository.set_follow_back(self.username, followers)

    def set_log(self, workpage_username, action, content_id=None, reference=None, insta_user_username=None):
        user_repository = repositories.InstaUserRepository()
        wp_repository = repositories.WorkPageRepository()
        insta_user, err = user_repository.get(Username=insta_user_username)
        wp, wp_err = wp_repository.get(Username=workpage_username)
        if wp:
            ac_log_repository = repositories.ActionLogRepository()
            ac_log = ac_log_repository.get_action_log(wp, action, content_id=content_id, reference=reference)
            ac_log_repository.add(ac_log)

    def get_comment_count(self, post_id):
        ac_log_repository = repositories.ActionLogRepository()
        comment_logs_count = ac_log_repository.get_action_log_count(self.workPage.WORK_PAGE_ID, Actions.CommentPost, post_id)
        return comment_logs_count

    def get_commentLike_count(self, post_id):
        ac_log_repository = repositories.ActionLogRepository()
        commentLike_logs_count = ac_log_repository.get_comentLikePage_count(self.workPage.WORK_PAGE_ID, post_id)
        return commentLike_logs_count

    def load_settings(self):
        repository = repositories.SettingRepository()
        setting, _ = repository.get(WorkPageId=self.workPage.WORK_PAGE_ID)
        self.setting = setting

    def get_proxy(self):
        repository = repositories.ProxyRepository()
        proxy, _ = repository.get(PROXY_ID=self.workPage.ProxyId)
        Proxy = collections.namedtuple('Proxy', 'Address Port Username Password')
        p = Proxy(proxy.Address, proxy.Port, proxy.Username, proxy.Password)
        return p

    def fetch_proxies(self):
        repository = repositories.ProxyRepository()
        results = requests.get("https://proxy.webshare.io/api/proxy/list/", headers={"Authorization": "Token ba7861bcafcfb854c7717a500fccd0144ddcb0a8"}).json()['results']
        proxy_list = []
        for i in results:
            valid = i['valid']
            if valid:
                ip = i['proxy_address'].strip()
                port = i['ports']['http']
                username = i['username'].strip()
                password = i['password'].strip()
                country = i['country_code'].strip()
                proxy = (ip, port, username, password, country)
                proxy_list.append(proxy)
        repository.add_proxy(proxy_list)


if __name__ == '__main__':
    import sys
    username = sys.argv[1]
    hide_browser = False
    if len(sys.argv) >= 3:
        if sys.argv[2].lower() == 'true':
            hide_browser = True
        elif sys.argv[2].lower() == 'false':
            hide_browser = False
    repository = repositories.WorkPageRepository()
    # wp, error = repository.get_workpage_by_username('gabrihcalderon')
    wp, error = repository.get_workpage_by_username(username)

    if not error:
        manager = BotManager(wp, hide_browser)
        # manager.fetch_proxies()
        manager.start()
