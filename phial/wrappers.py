class Command():
    def __init__(self, command, channel, args):
        self.command = command
        self.channel = channel
        self.args = args

    def __repr__(self):
        return "<Command: {0}, {1} in {2}>".format(self.command, self.args,
                                                   self.channel)


class Message():
    def __init__(self, text, channel):
        self.text = text
        self.channel = channel

    def __repr__(self):
        return "<Message: {0} in {1}>".format(self.text, self.channel)
