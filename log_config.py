LOG_SETTINGS = {
    'version': 1,
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console'],
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'normal',
            'filename': 'check_appointments.log',
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
            'stream': 'ext://sys.stdout'
        }
    },
    'formatters': {
        'normal': {
            'format': '%(asctime)s %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
}
