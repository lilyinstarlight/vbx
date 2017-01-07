class Device:
    def online(self):
        return None

    def dial(self, event, response):
        raise NotImplementedError

    def send(self, event, message, response):
        raise NotImplementedError
