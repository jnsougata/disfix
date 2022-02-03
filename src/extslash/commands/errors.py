class InvalidCog(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NonCoroutine(Exception):
    def __init__(self, message: str):
        super().__init__(message)
