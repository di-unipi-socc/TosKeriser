class TkException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class TkStackException(Exception):

    def __init__(self, *msg):
        self.stack = list(msg)

    def __str__(self):
        return '- ' + '\n- '.join(self.stack)
