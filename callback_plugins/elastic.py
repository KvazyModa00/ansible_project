from ansible.plugins.callback import CallbackBase
from elasticsearch import Elasticsearch
import datetime
import logging

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'elastic_logger'

    def __init__(self):
        super(CallbackModule, self).__init__()
        
        
        self.logger = logging.getLogger('ansible_elastic_logger')
        self.logger.setLevel(logging.ERROR)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.es = Elasticsearch(
            ['http://localhost:9200'],
            basic_auth=('elastic', '12345!@'),
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        self.playbook_start = None

    def v2_playbook_on_start(self, playbook):
        self.playbook_start = datetime.datetime.now()
        doc = {
            'event': 'playbook_start',
            'playbook': playbook._file_name,
            'timestamp': self.playbook_start.isoformat()
        }
        self.es.index(index='ansible-events', document=doc)

    def v2_runner_on_ok(self, result):
        doc = {
            'timestamp': datetime.datetime.now().isoformat(),
            'host': result._host.name,
            'task': result.task_name,
            'status': 'ok',
            'duration': {
                'start': self.playbook_start.isoformat(),
                'end': datetime.datetime.now().isoformat()
            }
        }
        self.es.index(index='ansible-tasks', document=doc)
    
    def v2_runner_on_failed(self, result, ignore_errors=False):
        doc = {
            'timestamp': datetime.datetime.now().isoformat(),
            'host': result._host.name,
            'task': result.task_name,
            'status': 'failed',
            'error': str(result._result.get('msg', 'No error message')),
            'ignore_errors': ignore_errors,
            'duration': {
                'start': self.playbook_start.isoformat() if self.playbook_start else None,
                'end': datetime.datetime.now().isoformat()
            }
        }
        self.es.index(index='ansible-tasks', document=doc)

    def v2_runner_on_unreachable(self, result):
        doc = {
            'timestamp': datetime.datetime.now().isoformat(),
            'host': result._host.name,
            'task': result.task_name,
            'status': 'unreachable',
            'error': str(result._result.get('msg', 'No error message')),
            'duration': {
                'start': self.playbook_start.isoformat() if self.playbook_start else None,
                'end': datetime.datetime.now().isoformat()
            }
        }
        self.es.index(index='ansible-tasks', document=doc)