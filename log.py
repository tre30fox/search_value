# coding = utf8


import time


class LogLevel(object):
    debug = 'DEBUG'
    info = 'INFO'
    warn = 'WARN'
    error = 'ERROR'
    systm = 'SYSTEM'

    @staticmethod
    def log(level, info):
        time_current = time.time()
        
        
        print('[{}][{}][{}][{}][{}] {}'.format())
