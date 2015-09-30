# encoding: utf8


import datetime
import time


def now():
    return datetime.datetime.now();


def formatDatetime(dt, fmt="%Y-%m-%d %H:%M:%S.%f"):
    return dt.strftime(fmt)


def parseToDatetime(dtStr, fmt="%Y-%m-%d %H:%M:%S.%f"):
    return datetime.datetime.strptime(dtStr, fmt)


def addDatetime(dt, weeks=0, days=0, hours=0, minutes=0, seconds=0, milliseconds=0, microseconds=0):
    delta = datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)
    dt += delta
    return dt


def timedeltaToSecond(dt):
    return dt.days * 24 * 60 * 60 + dt.seconds + dt.microseconds/1000000.0;


def timeDiffInSeconds(begin_time, end_time):
    return timedeltaToSecond(end_time - begin_time)



n = 2**24
d1 = datetime.datetime.now();
for x in xrange(n):
    d2 = datetime.datetime.now();
    if timedeltaToSecond(d2 - d1) > 1:
        d1 = d2;
        print(d2, x);




