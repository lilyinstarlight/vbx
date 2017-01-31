import vbx


class Say(vbx.Flow):
    def __init__(self, text, voice='woman', language='en', loop=1, **kwargs):
        self.text = text
        self.voice = voice
        self.language = language
        self.loop = loop

        super().__init__(**kwargs)

    def dial(self, event, response):
        response.say(self.text, voice=self.voice, language=self.language, loop=self.loop)

        self.completed = True
