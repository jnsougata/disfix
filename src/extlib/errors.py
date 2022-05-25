class InvalidCog(Exception):
    """
    Raised when a cog is not the correct type (extlib.Cog)
    """
    def __init__(self, message: str):
        super().__init__(message)


class NonCoroutine(Exception):
    """
    Raised when a function is not a coroutine
    """
    def __init__(self, message: str):
        super().__init__(message)


class CheckFailure(Exception):
    """
    Raised when a before invoke check fails
    """
    def __init__(self, message: str):
        super().__init__(message)


class ApplicationCommandError(Exception):
    """
    Raised when an application command fails to execute
    """
    def __init__(self, message: str):
        super().__init__(message)


class CommandNotImplemented(Exception):
    """
    Raised when a command is not implemented inside source
    """
    def __init__(self, message: str):
        super().__init__(message)


class CommandTypeMismatched(Exception):
    """
    Raised when a mismatch between two application command type is detected
    """
    def __init__(self, message: str):
        super().__init__(message)


class ReturnNotBoolean(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class BeforeInvokeJobFailure(Exception):
    """
    Raised when a before invoke job fails
    """
    def __init__(self, message: str):
        super().__init__(message)


class AfterInvokeJobFailure(Exception):
    """
    Raised when a before invoke job fails
    """
    def __init__(self, message: str):
        super().__init__(message)
