from abc import ABC, abstractmethod
from .context import ApplicationContext


class SlashCog(ABC):

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    async def command(self, ctx: ApplicationContext):
        pass

    @abstractmethod
    async def on_error(self, ctx: ApplicationContext, error: Exception):
        pass
