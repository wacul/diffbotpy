class DiffbotTokenError(KeyError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "DiffbotTokenError : {}".format(self.msg)


class DiffbotResponseError(IOError):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "DiffbotResponseError #{} :  {}".format(self.code, self.msg)


class DiffbotUnexpectedBodyError(Exception):
    def __init__(self, *args, **kwargs):
        self.raw = kwargs.pop("raw", None)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "DiffbotUnexpectedBodyError : {}".format(self.args[0])


class DiffbotJobStatusError(IOError):
    def __init__(self, status, msg):
        self.status = status
        self.msg = msg

    def __str__(self):
        return "DiffbotJobStatusError #{} :  {}".format(self.status, self.msg)
