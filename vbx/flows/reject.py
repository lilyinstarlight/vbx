import vbx


class Reject(vbx.Flow):
    def __init__(self, reason=None, **kwargs):
        self.reason = reason

        super().__init__(**kwargs)

    def dial(self, event, response):
        response.reject(self.reason)

        self.completed = True
