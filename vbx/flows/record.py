import vbx


class Record(vbx.Flow):
    def dial(self, event, response):
        response.record()

        self.completed = True
