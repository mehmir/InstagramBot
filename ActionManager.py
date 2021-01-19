import time
from RunSchedule import RunSchedule
import Bot.bot_config as config
from Bot.enums import Actions


class ActionManager:

    def __init__(self, action, hourly_average, is_blocked=False):
        self.action = action
        self.next_run = 0
        self.hourly_average = hourly_average
        self.is_blocked = False
        self.wait_for_block = config.wait_for_block

    def run_count(self):
        if self.next_run == 0:
            self.next_run = int(time.time())
        diff = int(time.time()) - self.next_run
        average_wait_second = RunSchedule.get_wait_average_second(self.hourly_average)
        if diff < 0:
            return 0
        elif diff < average_wait_second:
            return 1
        else:
            return round(diff/average_wait_second)

    def next(self):
        wait_time_second = RunSchedule.get_random_time_from_hourly_avreage(self.hourly_average)
        result = next(self.action)
        self.next_run = self.next_run + wait_time_second
        return result

    def set_next_run(self, hour=0, minute=0):
        next = int(time.time()) + RunSchedule.get_time_seconds(hours=hour, minutes=minute)
        self.next_run = next


    def set_action(self, action, is_blocked=False):
        if is_blocked:
            if self.is_blocked:
                self.wait_for_block += config.wait_for_already_block
            else:
                self.wait_for_block = config.wait_for_block
            self.is_blocked = True
            self.next_run = int(time.time()) + RunSchedule.get_time_seconds(self.wait_for_block)
        else:
            if self.is_blocked:
                self.wait_for_block = config.wait_for_block
                self.next_run = int(time.time()) + RunSchedule.get_time_seconds(self.wait_for_block)
            self.is_blocked = False
        self.action = action



