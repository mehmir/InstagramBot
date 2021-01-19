import random
from DAL import repositories
from DAL.models import ActivityTime
from Bot.enums import WeekDay
import datetime


class RunSchedule:

    def __init__(self, workpage):
        self.workpage = workpage
        self.time_activities = {}


    def get_time_activity(self):
        repository = repositories.ActivityTimeRepository()
        time_activities, _ = repository.where(ActivityTime.WorkPageId==self.workpage.WORK_PAGE_ID)
        for time in time_activities:
            days = WeekDay(time.Days)
            start_datetime = RunSchedule.convert_strtime_datetime(time.StartTime)
            end_datetime = RunSchedule.convert_strtime_datetime(time.EndTime)
            if start_datetime and end_datetime:
                for day in WeekDay:
                    if day in days and day != WeekDay.Nothing:
                        if day not in self.time_activities:
                            self.time_activities[day] = []
                        self.time_activities[day].append((start_datetime, end_datetime))

        for day in self.time_activities:
            self.time_activities[day].sort(key=lambda x: x[0])
            day_length = len(self.time_activities[day])
            time_list = self.time_activities[day]
            index = 0
            while index < day_length - 1:
                time = time_list[index]
                next_time = time_list[index + 1]
                if time[1] < next_time[0]:
                    index += 1
                elif time[1] < next_time[1]:
                    time_list[index] = (time_list[index][0], time_list[index + 1][1])
                    del time_list[index + 1]
                    day_length -= 1
                else:
                    del time_list[index + 1]
                    day_length -= 1

    def can_run(self):
        self.get_time_activity()
        weekday = WeekDay(int(2 ** (datetime.datetime.today().weekday())))
        day_time = datetime.datetime.today().time()
        date = RunSchedule.convert_strtime_datetime('{:02}:{:02}'.format(day_time.hour, day_time.minute))
        for time in self.time_activities[weekday]:
            if time[0] <= date <= time[1]:
                return True
        return False

    def next_run_time(self):
        weekday = WeekDay(int(2 ** (datetime.datetime.today().weekday())))
        today = datetime.datetime.today()
        day_time = today.time()
        date = RunSchedule.convert_strtime_datetime('{:02}:{:02}'.format(day_time.hour, day_time.minute))
        min = datetime.datetime.today().timestamp()
        min_index = None
        if weekday in self.time_activities:
            for i in range(len(self.time_activities[weekday])):
                if date < self.time_activities[weekday][i][0]:
                    if min > (self.time_activities[weekday][i][0] - date).total_seconds():
                        min_index = i
                        min = (self.time_activities[weekday][i][0] - date).total_seconds()
        if min_index is not None:
            return self.time_activities[weekday][min_index][0], (self.time_activities[weekday][min_index][0] - date).total_seconds()
        else:
            return (date + datetime.timedelta(days=1) - datetime.timedelta(hours=date.hour)),((date + datetime.timedelta(days=1) - datetime.timedelta(hours=date.hour)) - date).total_seconds()

    @staticmethod
    def get_random_time_from_hourly_avreage(hourly_average):
        m = RunSchedule.get_wait_average_second(hourly_average)
        return RunSchedule.get_random_time_from_seconds(30, 2*m + 30)

    @staticmethod
    def get_random_time_from_seconds(from_sec, to_sec):
        time = random.randint(from_sec, to_sec)
        return time

    @staticmethod
    def get_wait_average_second(hourly_average):
        return int(60 * 60 / hourly_average)

    @staticmethod
    def get_time_seconds(hours=0, minutes=0, seconds=0):
        return hours*3600 + minutes*60 + seconds

    @staticmethod
    def convert_strtime_datetime(time):
        try:
            t = time.split(':')
            dtime = datetime.datetime(100, 1, 1, int(t[0]), int(t[1]))
            return dtime
        except Exception:
            return None