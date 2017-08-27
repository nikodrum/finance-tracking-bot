import logging
from logging import config

LOGGING = {
    'version': 1,
    'formatters': {
        'precise': {
            'format': ('%(asctime)s %(process)-6d%(thread)-16d%(filename)-16s:'
                       '%(lineno)4d %(levelname)-6s: %(message)s'),
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'precise',
            'stream': 'ext://sys.stdout'
        },
        'fileHandler': {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "precise",
            "filename": './logs/stash.log',
            "maxBytes": 1024*1024*100,
        }
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'fileHandler']
        }
    }
}

config.dictConfig(LOGGING)
logger = logging.getLogger('root')
