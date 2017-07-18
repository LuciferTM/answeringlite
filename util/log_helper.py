import logging
import platform
from django.conf import settings
from django.utils.dictconfig import dictConfig

log_root_path = '/var/log/gikoo/'
if platform.system() == 'Windows':
    log_root_path = u'c:\\log\\'

def add_logger(logging, name):
    
    logging['handlers'][name] = {
                                'level':'DEBUG',
                                'class':'logging.handlers.RotatingFileHandler',
                                'filename': log_root_path + name + '.log',
                                'maxBytes': 1024*1024*10,
                                'backupCount': 10,
                                'formatter': 'verbose',
                                }
    logging['loggers'][name] = {
                                'handlers': ['console', name],
                                'level': 'DEBUG',
                                }
    
# _has_initialized = False
log_file_name_cache = []
def gikoo_logger(name=None):
    '''
    Just call gikoo_logger without name in most cases. But on commands under 
    'services/management/commands', please call it with a specified name at beginning 
    (before other import sentences). 
    For any new command, please add relative logging settings at settings.py
    '''
    global log_file_name_cache
    try:
        if name is None:
            name = settings.MAIN_LOG_NAME
        if name not in log_file_name_cache:
            add_logger(settings.LOGGING, name)
            dictConfig(settings.LOGGING)
        return logging.getLogger(name)
    except:
        return logging.getLogger(settings.MAIN_LOG_NAME)

