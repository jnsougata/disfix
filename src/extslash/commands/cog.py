from abc import ABC, abstractmethod
from .context import ApplicationContext
import sys
import traceback


class SlashCog(ABC):

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    async def command(self, ctx: ApplicationContext):
        pass

    async def on_error(self, ctx: ApplicationContext, error: Exception):
        """
        This method is called when an error is raised while executing a command.
        :param ctx: the application command context
        :param error: exception raised
        :return: Exception
        """
        print(f'Ignoring exception in command {ctx.command_name} (ID:{ctx.command_id})'
              f' from cog {self.__class__.__name__}', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        print(f'-----\n', file=sys.stderr)
