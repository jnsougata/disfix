from abc import ABC, abstractmethod
from .context import ApplicationContext


class SlashCog(ABC):

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    async def command(self, appctx: ApplicationContext):
        pass
