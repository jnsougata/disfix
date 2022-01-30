class CogNotFound(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidCog(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class SetupNotFound(Exception):
    def __init__(self, message: str):
        super().__init__(message)
