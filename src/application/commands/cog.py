from abc import ABC, abstractmethod
from .context import ApplicationContext


class SlashCog(ABC):

    def register(self):
        pass

    async def command(self, ctx: ApplicationContext):
        pass
