"""Enum of time ranges"""
from datetime import time
from enum import Enum


class TimeRanges(Enum):
    """Time ranges within a day
    A: 00:00:00 am - 07:29:59 am
    B: 07:30:00 am - 08:59:59 am
    C: 09:00:00 am - 05:59:59 pm
    D: 06:00:00 pm - 11:59:59 pm
    """

    A = (time.fromisoformat("00:00:00"), time.fromisoformat("07:29:59"), 7.5)
    B = (time.fromisoformat("07:30:00"), time.fromisoformat("08:59:59"), 1.5)
    C = (time.fromisoformat("09:00:00"), time.fromisoformat("17:59:59"), 9)
    D = (time.fromisoformat("18:00:00"), time.fromisoformat("23:59:59"), 6)

    def __init__(self, start_time: time, end_time: time, hours: float):
        self.start_time = start_time
        self.end_time = end_time
        self.hours = hours
