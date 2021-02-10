class TaskExp(object):

    def __init__(self, dao):
        self.dao = dao

    def run(self, dao, req):
        return 'hoge'