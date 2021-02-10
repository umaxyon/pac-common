# coding:utf-8
import os
import time

from celery import Celery
from celery.utils.log import get_task_logger

import mq
from common.dao import DB
from common.dao import Dao
from common.log import Log
from common.log import tracelog

app = Celery('mqpacpac',
             backend='rpc://',
             broker='amqp://mqpacpac:password@localhost:5672//')

os.environ['MECAB_CHARSET'] = 'utf-8'


class MqPacPac(object):

    def start(self, req):
        dao = Dao(DB())

        caller_name = req['caller']
        task_name = req['task']
        param = req['param']

        tasks_all = __import__("mq", fromlist=mq.__all__)
        task_mod = getattr(tasks_all, task_name)
        task_cls = getattr(task_mod, task_name)
        os.environ['LANG'] = 'ja_JP.UTF-8'
        if not os.name == 'nt':
            log_config = {
                'version': 1,
                'disable_existing_loggers': True,
                'formatters': {
                    'simple': {
                        'format': '%(asctime)s %(processName)-11s %(levelname)-5s %(message)s'
                    }
                },
                'handlers': {
                    'celery': {
                        'level': 'DEBUG',
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename': '/var/log/pacpac/mqpacpac.log',
                        'formatter': 'simple',
                        'mode': 'a',
                        'maxBytes': 1024 * 1024 * 5
                    }
                },
                'loggers': {
                    'celery': {
                        'handlers': ['celery'],
                        'level': 'DEBUG'
                    }
                }
            }
            from logging.config import dictConfig
            dictConfig(log_config)

            celery_logger = get_task_logger(task_name)
            # h = RotatingFileHandler('/var/log/pacpac/mqpacpac.log', 'a', (5 * 1024 * 1024), 5)
            # celery_logger.addHandler(h)

            Log.set_logger(celery_logger)

        task = task_cls(dao)
        Log.info('{} start!!!!!'.format(task_name))
        Log.info('param = {}'.format(param))

        return task.run(dao, req)


class MqCaller(object):
    def __init__(self, job_name):
        self.job_name = job_name

    @tracelog
    def call(self, task_name, param):
        return send_mq.delay({
            'caller': self.job_name,
            'task': task_name,
            'param': param
        })

    def call_wait(self, task_name, param, timeout=30):
        start = time.time()
        async_result = self.call(task_name, param)
        while not async_result.ready():
            if time.time() - start > timeout:
                raise Exception('timeout. {}'.format(task_name))
        return async_result.result


@app.task
def send_mq(req):
    return MqPacPac().start(req)
