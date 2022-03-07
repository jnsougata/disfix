class InvalidCog(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NonCoroutine(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class JobFailure(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ApplicationCommandError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class CommandNotImplemented(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TypeMismatch(Exception):
    def __init__(self, message: str):
        super().__init__(message)
