import logging.config

RMQ_HOST = 'localhost'
RMQ_PORT = 5672
RMQ_VHOST = '/'
RMQ_USERNAME = "guest"
RMQ_PASSWORD = "guest"
RMQ_INPUT_EXCHANGE = 'ex1'
RMQ_INPUT_QUEUE = 'q1'
RMQ_DEAD_EXCHANGE = 'exd'
RMQ_DEAD_QUEUE = 'qd'
RMQ_DEAD_TTL = 5 * 1000  # 5 секунд
RETRY_COUNT = 2

dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
}

logging.config.dictConfig(dict_config)