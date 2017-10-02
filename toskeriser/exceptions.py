class TosKeriserException(Exception):
    def __init__(self, *msg):
        self.stack = list(msg)

    def __str__(self):
        return '- ' + '\n- '.join(self.stack)
