from datetime import datetime, timedelta
from Bot.enums import Actions
import time
import RunSchedule
from DAL import repositories


class ActionLimitManager:

    def __init__(self, workpage_username, setting):
        hour, day, _ = ActionLimitManager.get_current_day_hour()
        h = {hour: ActionLimitManager.get_new_limits()}
        self.action_counts = {day: h}
        now = int(time.time())
        self.next_action_times = {Actions.CommentPost: now, Actions.LikeComment: now}
        self.limits = {}
        self.workpage_username = workpage_username
        self.set_limits(setting)
        self.init_action_counts(now)

    @staticmethod
    def get_new_limits():
        hour_action_counts = {}
        for action in Actions:
            hour_action_counts[action] = 0
        return hour_action_counts

    @staticmethod
    def get_current_day_hour():
        now = datetime.now()
        hour = now.hour
        day = now.day
        yesterday = (now - timedelta(days=1)).day
        return hour, day, yesterday

    def set_limits(self, setting):
        self.limits[Actions.Follow] = setting.MaxFollowsPerHour, setting.MaxCommentPerDay
        self.limits[Actions.UnFollow] = setting.MaxUnfollowsPerHour, setting.MaxUnfollowsPerDay
        self.limits[Actions.LikeComment] = setting.MaxLikeCommentsPerHour, setting.MaxLikeCommentsPerDay
        self.limits[Actions.LikePost] = setting.MaxLikePostsPerHour, setting.MaxLikePostsPerDay
        self.limits[Actions.CommentPost] = setting.MaxCommentPerHour, setting.MaxLikeCommentsPerDay
        self.limits[Actions.GetFollowers] = 1, 1


    def init_action_counts(self, now):
        repository = repositories.VActionCountRepository()
        action_counts = repository.get_action_count(self.workpage_username, now)

        for action_count in action_counts:
            day = action_count.Day % 100
            if day in self.action_counts:
                hour = action_count.Hour
                if hour not in self.action_counts[day]:
                    self.action_counts[day][hour] = ActionLimitManager.get_new_limits()
                self.action_counts[day][hour][action_count.ActionType] = action_count.Count



    def get_limits(self, action):
        return self.limits[action]

    def can_do_action(self, action):
        hour_count, day_count = self.get_action_count(action)
        hour_limit, day_limit = self.get_limits(action)

        return hour_count < hour_limit and day_count < day_limit

    def get_action_count(self, action):
        hour, day, yesterday = ActionLimitManager.get_current_day_hour()
        return self.get_action_count_by_date(action, hour, day, yesterday)

    def get_action_count_by_date(self, action, hour, day, yesterday):
        day_dict = self.action_counts.get(day, None)
        if day_dict:
            hour_dict = day_dict.get(hour, None)
            if hour_dict is None:
                self.action_counts[day][hour] = ActionLimitManager.get_new_limits()
        else:
            self.action_counts[day] = {hour: ActionLimitManager.get_new_limits()}
            self.action_counts.pop(yesterday, None)

        day_count = 0
        for h in self.action_counts[day]:
            day_count += self.action_counts[day][h][action]
        hour_count = self.action_counts[day][hour][action]

        return hour_count, day_count

    def set_action_count(self, action, increase):
        hour, day, yesterday = ActionLimitManager.get_current_day_hour()
        hour_count, _ = self.get_action_count_by_date(action, hour, day, yesterday)
        self.action_counts[day][hour][action] = hour_count + increase

    def set_action_time(self, action, hour):
        self.next_action_times[action] = int(time.time()) + RunSchedule.get_time_seconds(hour)

    def get_action_time(self, action):
        return self.next_action_times[action]


