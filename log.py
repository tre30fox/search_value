# coding = utf8


import time
import datetime
import inspect


class LogLevel(object):
    debug = 'DEBUG'
    info = 'INFO'
    warn = 'WARN'
    error = 'ERROR'
    systm = 'SYSTEM'


def log(level, msg):
    time_current = datetime.datetime.now()
    time_current_iso = time_current.isoformat()

    frame = inspect.currentframe()
    frame_info_list = inspect.getouterframes(frame)
    frame_info = frame_info_list[1][0]

    help(frame_info)
    print(type(frame_info), dir(frame_info), frame_info)
    # frame_info = inspect.getframeinfo(frame, context=2)

    # print('[{}][{}][{}][{}][{}]{}'.format(
    #     time_current_iso, level,
    #     frame_info.filename, frame_info.lineno, frame_info.function,
    #     msg))
