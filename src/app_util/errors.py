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


class NoGuildProvided(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TypeMismatch(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NameMismatch(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NameAlreadyExists(Exception):
    def __init__(self, message: str):
        super().__init__(message)
